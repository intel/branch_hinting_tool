from helpers import token_comment, update_in_string, tokenize_line
from global_var import GlobalVar
"""
Abstract class which defines the behaviour of the finite state machine on a file
"""


class FSM:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.run_state()

    def run_all(self, filename):

        tokens = []
        separators = ['(', ')', '\t', ' ','/*', '*/', '&&', '||']
        #separators = ['(',  ')', '\t', ' ', '&&', '||']
        #separators = ['(', '/*', '*/', ')',' ', '&&', '||']

        f = open(filename)
        print filename

        for line in f.readlines():

            #token line nu merge deocamdata
            #tokens = tokens + token_comment(line, separators)
            tokens = tokens + tokenize_line(line, separators)
        #for t in tokens:
         #  print t

        for token in tokens:
          #  print GlobalVar.in_preprocessor
            #print GlobalVar.in_string
            update_in_string(token)
            self.current_state = self.current_state.next_state(token)

