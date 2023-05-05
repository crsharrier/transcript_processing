
############################################################################
#METHODS FOR ADDING LaTeX TAGS
#return appropriate LaTeX tag for interruption line

def tag_routine(t):
    tag_spkr(t)
    tag_new_lines(t)
    remove_spaces(t)
    medskip(t)

#add \spkr{} command into each line in new_lines
def tag_spkr(t):
    for i in range(0, len(t.new_lines)):
        if t.speakers[i] != '':
            if not t.new_lines[i].startswith('*'):
                t.new_lines[i] = '\spkr{' + t.speakers[i] + '}' + t.new_lines[i]
            else:
                t.new_lines[i + 1] = '\spkr{' + t.speakers[i] + '}' + t.new_lines[i + 1]

def tag_interrupted(interrupted, n):
    if interrupted:
        return '\overmk{B' + str(n) + '}'
    else:
        return '\hspace{\offset{A1}{B' + str(n) + '}}'

#add tags to new_lines[]
def tag_new_lines(t):
    #place {A1} as anchor
    anchor = t.new_lines[0].find('}') + 1
    t.new_lines[0] = t.new_lines[0][:anchor] + '\overmk{A1}' + t.new_lines[0][anchor:]
    
    tag_n = 0
    #iterate over new_lines[]. Insert correct tag.
    for i in range(0, len(t.new_lines)):
        if t.interrupted[i]:
            j = 0
            overlap_count = 0
            while overlap_count < t.n_overlaps[i]:
                if overlap_count > 0 or t.interrupted[i][overlap_count]:
                    tag_n += 1
                while t.new_lines[i][j] != '[':
                    j += 1
                t.new_lines[i] = t.new_lines[i][:j] + tag_interrupted(t.interrupted[i][overlap_count], tag_n) + t.new_lines[i][j:]
                j += len(tag_interrupted(t.interrupted[i][overlap_count], tag_n)) + 1
                overlap_count += 1

        #rewind tag_n  
       # if t.interrupted[i]:
       #     tag_n -= t.n_overlaps[i - 2]
       # interrupted = not interrupted
    

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
