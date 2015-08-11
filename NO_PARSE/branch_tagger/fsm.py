from helpers import tokenize_line, update_in_string
from global_var import GlobalVar
"""
Abstract class which defines the behaviour of the finite state machine on a file
"""


class FSM:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.run_state()

    def run_all(self, filename):
        print "FSM-run_all"
        tokens = []
        separators = ['(', '/*', '*/', ')', '\t', ' ', '&&', '||']

        f = open(filename)
        #print filename

        for line in f.readlines():
            if "&&" in line or "||" in line or "if" in line or "while" in line or "for" in line:
                tokens = tokens + tokenize_line(line, separators)
            else:
                tokens += line

        #print tokens
        for token in tokens:
            update_in_string(token)
            self.current_state = self.current_state.next_state(token)

