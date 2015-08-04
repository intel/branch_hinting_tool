from states_impl import OutContext
from fsm import FSM


# Applies the finite state machine, starting from state OutContext

class ApplyFSMFile(FSM):
    def __init__(self):
        FSM.__init__(self, OutContext())
