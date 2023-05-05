#transcript class and methods

class Transcript:
    def __init__(self, path):
        self.path = path
        self.speaker_names = []

        self.lines = []
        self.new_lines = []
        self.speakers = []
        self.features = {}

        self.word_count = 0

#MEHTODS FOR INITIALISATION

    #error messaging
    def err_msg(self, id, line_n):
        if id == 1:
            print('Error: \'=\' found on consecutive lines > line', line_n)
        elif id == 2:
            print('Error: Unidentified equals sign', line_n)
        return 0
    
    #read file at self.path
    def read_file(self):
        with open(self.path, 'r') as f:
            content = f.read()
            self.lines = content.split('\n')

            self.new_lines = self.lines[1:]

    #return current speaker based on line
    def current_speaker(self, line):
        while self.speakers[line] == '':
            line -= 1
        return self.speakers[line]
    
    #calculate self.word_count and word_count for each speaker in features{}
    def count_words(self):
        for line in self.lines:
            self.word_count += (len(line.split()))
            
        for i in range(0, len(self.lines)):
            self.features[self.current_speaker(i)]['word_count'] += len(self.lines[i].split())

    #fill speakers[] list
    def get_speakers(self):
        self.speakers = [''] * (len(self.new_lines) + 1)
        x = 0
        self.speakers[0] = self.speaker_names[0]
        #Assign correct speaker names to speakers[], based on empty lines
        for line in range(0, len(self.new_lines)):
            if self.new_lines[line] == '' or self.new_lines[line].isspace():
                x = 1 if x == 0 else 0
                self.speakers[line + 1] = self.speaker_names[x]
        #add \spkr{} command into each line in new_lines
        for i in range(0, len(self.new_lines)):
            if self.speakers[i] != '':
                if not self.new_lines[i].startswith('*'):
                    self.new_lines[i] = '\spkr{' + self.speakers[i] + '}' + self.new_lines[i]
                else:
                    self.new_lines[i + 1] = '\spkr{' + self.speakers[i] + '}' + self.new_lines[i + 1]

    #initialise features{} dict for each speaker
    def init_features(self):
        self.speaker_names = [name for name in self.lines.pop(0).split()]
        for s in self.speaker_names:
            self.features[s] = {
            'interrupted_succ': 0,
            'interrupted_unsucc': 0,
            'overlapped': 0,
            
            'interruption_succ': 0,
            'interruption_unsucc': 0,
            'minimal_response': 0,
            'overlap': 0,

            'word_count': 0,
            'words_%': 0,
        }

#METHODS FOR INTERRUPTION TAGGING AND LOGGING

    #return correct type for a line containing =       
    def check_equals(self, i):
        curr = self.current_speaker(i)
        if self.lines[i].startswith('=') and self.lines[i].endswith('='):
            self.features[curr]['minimal_response'] += 1

    #return True if line ends with . ! or ?
    def terminated(self, line):
        if line.endswith('.') or line.endswith('!') or line.endswith('?'):
            return True
        return False

    #log appropriate kind of interruption in dict
    #is called when '[' is found on a given line
    def log_interruption(self, i, line, interrupted):
        curr = self.current_speaker(i)
        if interrupted:
            if line.endswith('='):
                if not self.terminated(self.lines[i + 2]):
                    self.features[curr]['interrupted_unsucc'] += 1
            if self.terminated(line):
                self.features[curr]['overlapped'] += 1
            elif line.endswith('-'):
                self.features[curr]['interrupted_succ'] += 1            
        else:
            if line.endswith('-'):
                self.features[curr]['interruption_unsucc'] += 1
            elif self.terminated(line):
                self.features[curr]['minimal_response'] += 1
            else:
                if (not self.terminated(self.lines[i - 2])):
                    self.features[curr]['interruption_succ'] += 1
                else:
                    self.features[curr]['overlap'] += 1

    def tag(self, interrupted, n):
        if interrupted:
            return '\overmk{B' + str(n) + '}'
        else:
            return '\hspace{\offset{A1}{B' + str(n) + '}}'

    def interruption_tagging(self):
        interrupted = True
        n = 0
        #place {A1} as anchor
        anchor = self.new_lines[0].find('}') + 1
        self.new_lines[0] = self.new_lines[0][:anchor] + '\overmk{A1}' + self.new_lines[0][anchor:]
        #iterate through rest of lines
        i = 0
        while i < len(self.new_lines):
            j = 0
            while j < len(self.new_lines[i]):
                interrupt_line = False
                if self.new_lines[i][j] == '[':
                    interrupt_line = True
                    #log interruptions for current_speaker
                    self.log_interruption(i, self.lines[i], interrupted)
                    #append LaTeX tag to line[i]
                    self.new_lines[i] = self.new_lines[i][:j] + self.tag(interrupted, n) + self.new_lines[i][j:]
                    j += len(self.tag(interrupted, n))
                if interrupt_line:
                    #switch 'interrupted' to allow for second '[' on same line
                    interrupted = not interrupted
                    #update \overmk tag number ({B28} etc)
                    if interrupted:
                        n += 1
                else:
                    self.check_equals(i)
                j += 1
            i += 1
        
    #METHODS FOR CLEANING 

    #remove spaces at the start of line (after speaker tag)
    def remove_spaces(self):
        for i in range(0, len(self.new_lines)):
            if self.new_lines[i] and not self.new_lines[i].isspace():
                if self.new_lines[i].startswith('\\spkr'):
                    j = 0
                    while self.new_lines[i][j] != '}':
                        j += 1
                    k = j + 1
                else:
                    k = 0
                while self.new_lines[i][k] == ' ':
                    k += 1
                if self.new_lines[i].startswith('\\spkr'):
                    self.new_lines[i] = self.new_lines[i][:j + 1] + self.new_lines[i][k:]
                else:
                    self.new_lines[i] = self.new_lines[i][k:]

    #\medskip for empty lines
    def medskip(self):
        for line in range(0, len(self.new_lines)):
            if self.new_lines[line] == '' or self.new_lines[line].isspace():
                self.new_lines[line] = '\medskip'

    #METHOD WHICH CALLS ABOVE FUNCTIONS
    def process_transcript(self):
        #initialise
        self.read_file()
        self.init_features()
        self.get_speakers()
        self.count_words()
        #process
        self.interruption_tagging()
        self.remove_spaces()
        self.medskip()
        #self.write_new_file()