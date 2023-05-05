#MEHTODS FOR INITIALISATION
#after init_routine:
    # 


def init_routine(t):
    read_file(t)
    init_features(t)
    get_speakers(t)
    count_words(t)
    get_interrupted(t)

#save each line at t.path to lines[]
#check for consecutive empty lines and remove empty lines at end
#new_lines = lines[1:]
def read_file(t):
    with open(t.path, 'r') as f:
        content = f.read()
        t.lines = content.split('\n')
    t.lines = [line.rstrip().lstrip() for line in t.lines] 
    #check for consecutive empty lines
    for i in range(0, len(t.lines) - 1):
        if t.lines[i].isspace() or not t.lines[i]:
            if t.lines[i + 1].isspace() or not t.lines[i + 1]:
                raise Exception("Consecutive empty lines found in:", t.path, "line no.", i)
    #delete empty lines at end of list
    j = len(t.lines) - 1
    while t.lines[j].isspace() or not t.lines[j]:
        t.lines.pop(j)
        j -= 1 
    t.new_lines = t.lines[1:]

#fill speaker_names[] from lines[0], and pop lines[0]
#initialise features{} dict for each speaker

def init_features(t):
    t.speaker_names = [name for name in t.lines.pop(0).split()]
    for s in t.speaker_names:
        t.features[s] = {
        'interrupted_succ': 0,
        'interrupted_unsucc': 0,
        'overlapped': 0,
        
        'interruption_succ': 0,
        'interruption_unsucc': 0,
        'overlap': 0,
        
        'minimal_response': 0,

        'word_count': 0,
        'words_%': 0,
    }
        
#fill speakers[] list, switching speaker after an empty line
def get_speakers(t):
    t.speakers = [''] * len(t.new_lines)
    x = 0
    t.speakers[0] = t.speaker_names[0]
    #Assign correct speaker names to speakers[], based on empty lines
    for line in range(0, len(t.new_lines)):
        if t.new_lines[line] == '' or t.new_lines[line].isspace():
            x = 1 if x == 0 else 0
            t.speakers[line + 1] = t.speaker_names[x]


#calculate t.word_count and word_count for each speaker in features{}
def count_words(t):
    for line in t.lines:
        t.word_count += (len(line.split()))
        
    for i in range(0, len(t.lines)):
        t.features[t.current_speaker(i)]['word_count'] += len(t.lines[i].split())

    for speaker in t.features:
            t.features[speaker]['words_%'] = (t.features[speaker]['word_count'] / t.word_count) * 100


#assign n_overlaps[] 
#assign interrupted[] 
def get_interrupted(t):
    #calculate and assign n_overlaps[].
    t.n_overlaps = [0] * len(t.lines)
    for i in range(0, len(t.lines)):
        t.n_overlaps[i] = t.overlap_count(t.lines[i]) 
    #initialise interrupted[]
    t.interrupted = [['']] * len(t.lines)
    for i in range(0, len(t.interrupted)):
        t.interrupted[i] = [''] * t.n_overlaps[i]

    interrupted = True
    for i in range(0, len(t.lines)):
        overlap_count = 0
        overlap_line = False
        for j in range(0, len(t.lines[i])):
            if t.lines[i][j] == '[':
                overlap_line = True
                overlap_count += 1
                if i > 1 and overlap_count > 1:
                    if not t.lines[i - 1] and overlap_count > t.n_overlaps[i - 2]:
                        interrupted = not interrupted
                t.interrupted[i][overlap_count - 1] = interrupted
        if overlap_line:
            interrupted = not interrupted
        

