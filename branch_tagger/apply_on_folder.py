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

def clean():
    GlobalVar = global_var.GlobalVar()
    modified_text = StringIO()

    count_paren = 1

    if_condition = False
    while_condition = False
    for_condition = False

    in_preprocessor = False
    in_string = False

    in_comment = False

    comment = False

    condition = StringIO()
    return GlobalVar

def apply_on_folder(target, ofile, blacklist):
    global GlobalVar

    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):

            if item not in blacklist:
                apply_on_folder(target + "/" + item, ofile, blacklist)
            else:
                print "Blacklisted folder: " + item
        #elif (item.endswith(".c") or item.endswith(".h") or item.endswith(".cpp")) and item not in blacklist:
        elif (item.endswith(".c") or item.endswith(".h") or item.endswith(".cpp")) and item not in blacklist:
        #elif item.endswith(".cpp") and item not in blacklist:
            GlobalVar = global_var.GlobalVar()

            #GlobalVar = clean()

            print "#-----------------------------------------------------------------------------------------"
            print len(global_var.GlobalVar.modified_text.getvalue()), ' ', len(global_var.GlobalVar.condition.getvalue())
            print "#-----------------------------------------------------------------------------------------"

            global_var.GlobalVar.modified_text = StringIO()

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

#apply(sys.argv[1], sys.argv[2])
