from helpers import update_in_string, tokenize_line

from global_var import GlobalVar
"""
Abstract class which defines the behaviour of the finite state machine.
"""


class FSM:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.run_state()

    def run_all(self, filename):

        tokens = []
        separators = ['(', ')', '\t', ' ', '/*', '*/', '&&', '||']

        f = open(filename)
        print filename
        line_no = 0
        for line in f.readlines():
            line_no += 1
            fresh_tokens = tokenize_line(line, separators)

            token_tuple = []
            for i in xrange(len(fresh_tokens)):
                token_tuple.append([fresh_tokens[i], line_no])
                #print token_tuple[i][1]

            #tokens = tokens + fresh_tokens
            tokens = tokens + token_tuple
        for token in tokens:
            update_in_string(token[0])
            self.current_state = self.current_state.next_state(token)

