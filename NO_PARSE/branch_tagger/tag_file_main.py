from global_var import GlobalVar
from apply_fsm_file import ApplyFSMFile

import sys

def main():
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]

    ApplyFSMFile().run_all(inputfile)

    f_tagged = open(outputfile, 'w+')
    f_tagged.write(GlobalVar.modified_text)


if __name__ == '__main__':
    main()
