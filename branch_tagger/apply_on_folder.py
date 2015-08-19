import os
import time

import tag_file
import global_var

"""
Performs tagging on all the files ending in .c and .h from a folder given as argument in command line.
It creates a temporary folder TmpFolder where the output is deposited, then all the files in
TmpFolder replace those in the original folder. The TmpFolder will be deleted.
"""


def applyOnFolder(target, ofile):

    #print target
    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):
            #print target
            applyOnFolder(target + "/" + item, ofile)
        elif (item.endswith(".c") or item.endswith(".h")) and item != "data_file.c":
            global_var.GlobalVar.modified_text = ""
            #command = "python tag_file.py " + item + " " + item + "_copy"
            start = time.time()
            print  "Start on: " + item
            tag_file.tag(item, item + "_copy")
            end = time.time()
            #os.system(command)
            command = "cp " + item + "_copy " + item
            os.system(command)
            command = "rm " + item + "_copy "
            os.system(command)

            s = target + "/" + item + ", " + str(round(end-start, 2))
            ofile.write(s)
            print s

    os.chdir(old_path)


def apply(target):
    try:
        ofile = open(target + "/parse_time.csv", 'w')
    except:
        print "parse_time.csv: error opening file for write\n"
        raise
    s = "FILENAME, EXECUTION TIME(s)"
    ofile.write(s)

    path_input = target
    if os.path.isdir(path_input):
        applyOnFolder(path_input, ofile)
    else:
        tag_file.tag(path_input, path_input)

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
        command = 'python' + " " + 'tag_file.py' + " " + path_input + " " + path_input
        os.system(command)

if __name__ == '__main__':
    main()
"""