#METHODS FOR CALCULATING OVERLAPS
#returns number of [overlaps in a given line

def overlap_routine(t):
    get_overlaps(t)
    populate_features(t)

#read overlap_list[] and update features{} accordingly
def populate_features(t):
    for i in range(0, len(t.overlap_list)):
        for type in t.overlap_list[i]:
            if type in t.features[t.current_speaker(i)]:
                t.features[t.current_speaker(i)][type] += 1


#return correct overlap type given 'interruption' and final_symbol
def lookup_symbol(symbol, interrupted):
    interrupted_dict = {
        'interrupted_succ': ['-'],
        'overlapped': ['?', '!', '.'],
        'interrupted_unsucc': ['=', '['],
    }
    interruption_dict = {
        'interruption_unsucc': ['-'],
        'interruption_succ': ['', '['],
        'minimal_response': ['?', '!', '.'],
    }
    dict = interrupted_dict if interrupted else interruption_dict
    for key in dict:
        if symbol in dict[key]:
            return key
    return 'error'

#after overlap.list[] has been populated do a second pass,
#correcting for instances of 'overlap' and '=minimal response='
def correct_overlaps(t):
    for i in range(0, len(t.overlap_list)):
        if t.overlap_list[i]:
            if t.overlap_list[i - 2] and t.overlap_list[i - 2][-1] == 'overlapped' and t.overlap_list[i][0] == 'interruption_succ':
                t.overlap_list[i][0] = 'overlap'
        if t.lines[i].startswith('=') and t.lines[i].endswith('=') and not t.n_overlaps[i]:
            t.overlap_list[i] = ['minimal_response']
    for i in range(0, len(t.overlap_list)):
        if t.overlap_list[i]:
            if t.overlap_list[i - 2] and t.overlap_list[i - 2][-1] == 'interrupted_unsucc' and t.overlap_list[i][0] == 'minimal_response':
                t.overlap_list[i - 2].pop(-1)

#assign overlap_list        
def get_overlaps(t):
    #initialise overlap_list[]
    t.overlap_list = [['']] * len(t.lines)
    for i in range(0, len(t.overlap_list)):
        t.overlap_list[i] = [''] * t.n_overlaps[i]
    
    #iterate over interrupted[]
    for i in range(0, len(t.interrupted)):
        if t.interrupted[i]:
            for j in range(0, len(t.interrupted[i])):
                t.overlap_list[i][j] = lookup_symbol(t.final_symbol(i, j), t.interrupted[i][j])
    correct_overlaps(t)