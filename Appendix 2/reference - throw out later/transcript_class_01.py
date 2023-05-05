#transcript class and methods

class Transcript:
    def __init__(self, path):
        self.path = path
        self.speaker_names = []

        self.lines = []
        self.new_lines = []
        self.speakers = []
        self.features = {}
        self.interrupted = []

        self.n_overlaps = []
        self.overlap_list = []

        self.word_count = 0

############################################################################
#MEHTODS FOR INITIALISATION
    #read file at self.path. 
    #Save each line to lines
    #Check for consecutive empty lines and remove empty lines at end
    #new_lines = lines[1:]
    def read_file(self):
        with open(self.path, 'r') as f:
            content = f.read()
            self.lines = content.split('\n')
        self.lines = [line.rstrip().lstrip() for line in self.lines] 
        #check for consecutive empty lines
        for i in range(0, len(self.lines) - 1):
            if self.lines[i].isspace() or not self.lines[i]:
                if self.lines[i + 1].isspace() or not self.lines[i + 1]:
                    raise Exception("Consecutive empty lines found in:", self.path, "line no.", i)
        #delete empty lines at end of list
        j = len(self.lines) - 1
        while self.lines[j].isspace() or not self.lines[j]:
            self.lines.pop(j)
            j -= 1 
        self.new_lines = self.lines[1:]

    #fill speaker_names[] from lines[0], and pop lines[0]
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

    #return current speaker based on line number
    def current_speaker(self, i):
        while self.speakers[i] == '':
            i -= 1
        return self.speakers[i]
    
    #fill speakers[] list, switching speaker after an empty line
    #add \spkr{} tag to new_lines
    def get_speakers(self):
        self.speakers = [''] * len(self.new_lines)
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

    #calculate self.word_count and word_count for each speaker in features{}
    def count_words(self):
        for line in self.lines:
            self.word_count += (len(line.split()))
            
        for i in range(0, len(self.lines)):
            self.features[self.current_speaker(i)]['word_count'] += len(self.lines[i].split())

############################################################################
#METHODS FOR CALCULATING OVERLAPS
    #returns number of [overlaps in a given line
    def overlap_count(self, line):
        count = 0
        for letter in line:
            if letter == '[':
                count += 1
        return count   

    #if line[i] isn't the last '[', return '[', else, return final symbol
    def final_symbol(self, i, n_overlaps):
        result = [''] * n_overlaps
        n = 1
        j = 0
        symbols = ['-', '?', '!', '.', '=']
        while self.lines[i][j] != '[':
            j += 1
        j += 1
        while j < len(self.lines[i]):
            if self.lines[i][j] == '[':
                k = j - 1
                while self.lines[i][k].isspace():
                    k -= 1
                return '-' if self.lines[i][k] == '-' else '['
            j += 1
        for sym in symbols:
            if self.lines[i].endswith(sym):
                return sym
        return ''

    #return correct overlap type given 'interruption' and final_symbol
    def lookup_symbol(self, symbol, interrupted):
        interrupted_dict = {
            'interrupted_succ': ['-'],
            'overlapped': ['?', '!', '.'],
            'interrupted_unsucc': ['=', '['],
        }
        interruption_dict = {
            'interruption_unsucc': ['-'],
            'interruption_succ': ['', '['],
            'minimal_response': ['?', '!', '.'],
            'overlap': [],
        }
        dict = interrupted_dict if interrupted else interruption_dict
        for key in dict:
            if symbol in dict[key]:
                return key
        return 'error'

    #after overlap.list[] has been populated do a second pass,
    #correcting for instances of 'overlap' and '=minimal response='
    def correct_overlaps(self):
        for i in range(0, len(self.overlap_list)):
            if self.overlap_list[i][-1] == 'overlapped':
                self.overlap_list[i + 2][0] = 'overlap'
            if self.lines[i].startswith('=') and self.lines[i].endswith('='):
                self.overlap_list[i] = ['minimal_response']
        for i in range(0, len(self.overlap_list)):
            if self.overlap_list[i][-1] == 'interrupted_unsucc' and self.overlap_list[i + 2][0] == 'minimal_response':
                self.overlap_list[i].pop(-1)

    #fill interrupted[] 
    def log_interrupted(self):
        #calculate and assign n_overlaps[]. Initialise overlap_list[]
        self.n_overlaps = [0] * len(self.lines)
        self.overlap_list = [['']] * len(self.lines)
        for i in range(0, len(self.lines)):
            self.n_overlaps[i] = self.overlap_count(self.lines[i]) 
        #iterate over self.lines. log interrupts type if '[' is found
        self.interrupted = [['']] * len(self.lines)
        interrupted = True
        for i in range(0, len(self.lines)):
            overlap_count = 0
            overlap_line = False
            for j in range(0, len(self.lines[i])):
                if self.lines[i][j] == '[':
                    overlap_line = True
                    overlap_count += 1
                    if i > 1 and overlap_count > 1:
                        if not self.lines[i - 1] and overlap_count > self.n_overlaps[i - 2]:
                            interrupted = not interrupted
                    if not self.interrupted[i][0]:
                        self.interrupted[i] = [interrupted]
                    else:
                        self.interrupted[i] += [interrupted]
            if overlap_line:
                interrupted = not interrupted

    #assign overlap_list        
    def log_overlaps(self):
        #iterate over self.lines. lookup_symbol if '[' is found
        interrupted = True
        for i in range(0, len(self.interrupted)):
            if self.interrupted[i]:
                for j in self.interrupted[i]:
                    self.overlap_list[i][j] = [self.lookup_symbol(self.final_symbol(i, self.n_overlaps), self.interrupted[i])]
            
            
            
            
            overlap_count = 0
            overlap_line = False
            for j in range(0, len(self.lines[i])):
                if self.lines[i][j] == '[':
                    overlap_line = True
                    overlap_count += 1
                    if i > 1 and overlap_count > 1:
                        if not self.lines[i - 1] and overlap_count > self.n_overlaps[i - 2]:
                            interrupted = not interrupted
                    if not self.overlap_list[i][0]:
                        self.overlap_list[i] = [self.lookup_symbol(self.final_symbol(i, j), interrupted)]
                    else:
                        self.overlap_list[i] += [self.lookup_symbol(self.final_symbol(i, j), interrupted)]
            if overlap_line:
                interrupted = not interrupted
        self.correct_overlaps()

    #read overlap_list[] and update features{} accordingly
    def populate_features(self):
        for i in range(0, len(self.overlap_list)):
            for type in self.overlap_list[i]:
                if type in self.features[self.current_speaker(i)]:
                    self.features[self.current_speaker(i)][type] += 1

############################################################################
#METHODS FOR ADDING LaTeX TAGS
    #return appropriate LaTeX tag for interruption line
    def tag(self, interrupted, n):
        if interrupted:
            return '\overmk{B' + str(n) + '}'
        else:
            return '\hspace{\offset{A1}{B' + str(n) + '}}'
    
    #add tags to new_lines[]
    def tag_new_lines(self):
        n = 0
        #place {A1} as anchor
        anchor = self.new_lines[0].find('}') + 1
        self.new_lines[0] = self.new_lines[0][:anchor] + '\overmk{A1}' + self.new_lines[0][anchor:]
        interrupted = True
        for i in range(0, len(self.lines)):
            overlap_count = 0
            overlap_line = False
            for j in range(0, len(self.lines[i])):
                if self.lines[i][j] == '[':
                    overlap_line = True
                    overlap_count += 1
                    if i > 1 and overlap_count > 1:
                        if not self.lines[i - 1] and overlap_count > self.n_overlaps[i - 2]:
                            interrupted = not interrupted
                        n += 1
                    if i > 1:
                        if overlap_count > self.n_overlaps[i - 2]:
                            interrupted = not interrupted
                    #append LaTeX tag to line[i]
                    self.new_lines[i] = self.new_lines[i][:j] + self.tag(interrupted, n) + self.new_lines[i][j:]
            if overlap_line:
                #update \overmk tag number ({B28} etc)
                if interrupted:
                    n -= self.n_overlaps[i - 1]
                interrupted = not interrupted


############################################################################
#METHOD WHICH CALLS OTHER METHODS IN ORDER,
#'FILLING' THE CLASS INSTANCE
    def process_transcript(self):
        #initialise
        self.read_file()
        self.init_features()
        self.get_speakers()
        self.count_words()
        #process
        self.log_interrupted()
        self.log_overlaps()
        self.populate_features()
        self.tag_new_lines()
        self.remove_spaces()
        self.medskip()





#METHODS FOR INTERRUPTION TAGGING AND LOGGING

    #log minimal_response for a line =like this=. 
    #is only called if not overlap_line 
    """   
    def check_equals(self, i):
        curr = self.current_speaker(i)
        if self.lines[i].startswith('=') and self.lines[i].endswith('='):
            self.features[curr]['minimal_response'] += 1
            print(print('i = ', i, '=minimal_response=', 'line = ', self.new_lines[i]))

    #return True if line ends with . ! or ?
    def terminated(self, line):
        if line.endswith('.') or line.endswith('!') or line.endswith('?'):
            return True
        return False

    #return appropriate interruption type.
    #is called when '[' is found on a given line
    def log_interruption(self, i, interrupted):
        if interrupted:
            if self.lines[i].endswith('='):
                if not self.terminated(self.lines[i + 2]):
                    return 'interrupted_unsucc'
            if self.terminated(self.lines[i]):
                return 'overlapped'
            elif self.lines[i].endswith('-'):
                return'interrupted_succ'           
        else:
            if self.lines[i].endswith('-'):
                return 'interruption_unsucc'
            elif self.terminated(self.lines[i]):
                return 'minimal_response'
            else:
                if (not self.terminated(self.lines[i - 2])):
                    return 'interruption_succ'
                else:
                    return 'overlap'
     """     
    

    #place {A1} tag
    """
    def interruption_logging(self):
        interrupted = True
        n = 0
        #iterate through rest of lines
        i = 0
        while i < len(self.new_lines):
            j = 0
            while j < len(self.new_lines[i]):
                overlap_line = False
                if self.new_lines[i][j] == '[':
                    curr = self.current_speaker(i)
                    overlap_line = True
                    #log interruptions for current_speaker
                    print('i = ', i, self.log_interruption(i, interrupted), 'line = ', self.new_lines[i])
                    self.features[curr][self.log_interruption(i, interrupted)] += 1
                if overlap_line:
                    #switch 'interrupted' to allow for second '[' on same line
                    interrupted = not interrupted
                else:
                    self.check_equals(i)
                j += 1
            i += 1

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
                overlap_line = False
                if self.new_lines[i][j] == '[':
                    overlap_line = True
                    #append LaTeX tag to line[i]
                    self.new_lines[i] = self.new_lines[i][:j] + self.tag(interrupted, n) + self.new_lines[i][j:]
                    j += len(self.tag(interrupted, n))
                if overlap_line:
                    #switch 'interrupted' to allow for second '[' on same line
                    interrupted = not interrupted
                    #update \overmk tag number ({B28} etc)
                    if interrupted:
                        n += 1
                else:
                    self.check_equals(i)
                j += 1
            i += 1
    """  
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

    
