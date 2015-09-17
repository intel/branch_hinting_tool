import os
import time
import sys

import tag_file
import global_var
from cStringIO import StringIO

"""
Performs tagging on all the files ending in .c and .h from a folder given as argument.
Also, it does not tag the files in a given black list.
"""


def apply_on_folder(target, ofile, blacklist):
    global GlobalVar

    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.islink(item):
            print item + " is link"
        elif os.path.isdir(item) and os.path.islink(item) is False:

            if item not in blacklist:
                apply_on_folder(target + "/" + item, ofile, blacklist)
            else:
                print "Blacklisted folder: " + item

        elif (item.endswith(".c") or item.endswith(".h") or item.endswith(".cpp")) and item not in blacklist:

            GlobalVar = global_var.GlobalVar()

            global_var.GlobalVar.modified_text = StringIO()

            print "Parsing " + os.path.join(target, item) + " ..."
            start = time.time()
            tag_file.tag(item, item + "_copy")
            end = time.time()
            command = "cp " + item + "_copy " + item
            os.system(command)
            command = "rm " + item + "_copy "
            os.system(command)

            s = target + "/" + item + ", " + str(round(end - start, 2))
            ofile.write(s)
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
    path_input = target
    if os.path.isdir(path_input):
        apply_on_folder(path_input, ofile, blacklist)
    else:
        tag_file.tag(path_input, path_input)


#apply(sys.argv[1], sys.argv[2])
