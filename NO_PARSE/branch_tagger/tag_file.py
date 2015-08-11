from global_var import GlobalVar
from apply_fsm_file import ApplyFSMFile

import sys

"""
 Performs tagging on a file given as argument in command line,
 creates a string representing the tagged file and outputs it
 in a file given as argument.
"""

def tag(input, output):

    ApplyFSMFile().run_all(input)

    f_tagged = open(output, 'w+')
    f_tagged.write(GlobalVar.modified_text)

