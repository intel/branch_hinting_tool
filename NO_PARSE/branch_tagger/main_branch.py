#!/usr/bin/env python
import os
import sys

"""
Performs tagging on all the files ending in .c and .h from a folder given as argument in command line.
It creates a temporary folder TmpFolder where the output is deposited, then all the files in
TmpFolder replace those in the original folder. The TmpFolder will be deleted.
"""


def main():
    path_input = sys.argv[1]
    if os.path.isdir(path_input):
        path_output = path_input + "TmpFolder/"
        make_directory_command = "mkdir" + " " + path_output
        os.system(make_directory_command)

        # OriginalFolderCopy contains the original folder, before it is modified
        make_directory_copy = "mkdir" + " " + path_input.rstrip("/") + "Copy/"
        os.system(make_directory_copy)
        command_cp = "cp" + " " + "-r" + " " + path_input + " " + path_input.rstrip("/") + "Copy/"
        os.system(command_cp)

        for filename in os.listdir(path_input):
            if filename.endswith('.c') or filename.endswith('.h'):
                command = 'python' + " " + 'tag_file.py' + " " + path_input + filename + " " + path_output + filename
                os.system(command)

        command = "cp" + " " + path_output + "*" + " " + path_input
        os.system(command)

        remove_command = "rm" + " " + "-r" + " " + path_output
        os.system(remove_command)
    elif os.path.isfile(path_input):
        command_cp = "cp" + " " + "-r" + " " + path_input + " " + path_input.rstrip("/") + "_copy"
        os.system(command_cp)
        command = 'python' + " " + 'tag_file_main.py' + " " + path_input + " " + path_input + "_out"
        print command
        errc = os.system(command)


if __name__ == '__main__':
    main()
