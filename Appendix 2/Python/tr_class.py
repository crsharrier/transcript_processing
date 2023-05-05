#transcript class and methods

from Python.tr_init import *
import pandas as pd

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
#UTILITY METHODS
    #return number of '[' found in line
    def overlap_count(self, line):
        count = 0
        for letter in line:
            if letter == '[':
                count += 1
        return count   

    #return current speaker based on line number
    def current_speaker(self, i):
        while self.speakers[i] == '':
            i -= 1
        return self.speakers[i]
   
    #if line[i] isn't the last '[', return '[', else, return final symbol
    def final_symbol(self, i, index):
        symbols = ['-', '?', '!', '.', '=']
        if self.n_overlaps[i] == 1 or self.n_overlaps[i] == index + 1:
            for sym in symbols:
                if self.lines[i].endswith(sym):
                    return sym
            return ''
        n = 1
        j = 0
        while n < (self.n_overlaps[i] - index):
            while self.lines[i][j] != '[':
                j += 1
            n += 1
        j += 1
        while j < len(self.lines[i]):
            if self.lines[i][j] == '[':
                k = j - 1
                while self.lines[i][k].isspace():
                    k -= 1
                return '-' if self.lines[i][k] == '-' else '['
            j += 1


############################################################################
#CREATE DATAFRAMES
    #create transcript_df and features_df
    def create_df(self, full=False):
        d = {
            'Speakers': self.speakers,
            'Lines': self.lines,
            'Overlap Type(s)': self.overlap_list,
            'Interrupted?': self.interrupted,
            'Overlap Count': self.n_overlaps,
            }
            
        self.transcript_df = pd.DataFrame(d)
        self.features_df = pd.DataFrame(self.features)
        self.features_df = self.features_df.astype(int)
        
