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

        for line in f.readlines():
            tokens = tokens + tokenize_line(line, separators)

        for token in tokens:
            update_in_string(token)
            self.current_state = self.current_state.next_state(token)
