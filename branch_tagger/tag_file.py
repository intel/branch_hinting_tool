from global_var import GlobalVar
from apply_fsm_file import ApplyFSMFile


"""
 Performs tagging on a file given as argument, creates a string representing the tagged file
 and outputs it in a file given as argument.
"""


def tag(input, output):
    ApplyFSMFile().run_all(input)

    f_tagged = open(output, 'w+')
    #print "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    #print GlobalVar.modified_text.getvalue()
    #print "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    f_tagged.write(GlobalVar.modified_text.getvalue())
    GlobalVar.modified_text.truncate(0)
    f_tagged.close()
