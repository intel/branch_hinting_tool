from global_var import GlobalVar
from apply_fsm_file import ApplyFSMFile

import sys

"""
 Performs tagging on a file given as argument in command line,
 creates a string representing the tagged file and outputs it
 in a file given as argument.
"""


def tag(input, output):
    inputfile = input
    outputfile = output

    ApplyFSMFile().run_all(inputfile)

    f_tagged = open(outputfile, 'w+')
    f_tagged.write(GlobalVar.modified_text)

    f_tagged.close()
