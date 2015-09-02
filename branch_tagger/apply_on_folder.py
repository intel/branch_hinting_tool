import os
import time

import tag_file
import global_var

"""
Performs tagging on all the files ending in .c and .h from a folder given as argument.
Also, it does not tag the files in a given black list.
"""


def apply_on_folder(target, ofile, blacklist):
    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):

            if item not in blacklist:
                apply_on_folder(target + "/" + item, ofile, blacklist)
            else:
                print "Blacklisted folder: " + item
        elif (item.endswith(".c") or item.endswith(".h")) and item not in blacklist:

            global_var.GlobalVar.modified_text = ""

            start = time.time()
            print "Start on: " + item
            tag_file.tag(item, item + "_copy")
            end = time.time()
            command = "cp " + item + "_copy " + item
            os.system(command)
            command = "rm " + item + "_copy "
            os.system(command)

            s = target + "/" + item + ", " + str(round(end - start, 2))
            ofile.write(s)
            print s

        elif (item.endswith(".c") or item.endswith(".h")) and item in blacklist:
            print "Blacklisted: " + item
    os.chdir(old_path)


def apply(target, blacklist):
    try:
        ofile = open(target + "/parse_time.csv", 'w')
    except:
        print "parse_time.csv: error opening file for write\n"
        raise
    s = "FILENAME, EXECUTION TIME(s)"
    ofile.write(s)
    print blacklist
    path_input = target
    if os.path.isdir(path_input):
        apply_on_folder(path_input, ofile, blacklist)
    else:
        tag_file.tag(path_input, path_input)


