############################################################################
# Branch Hinting Tool
#
# Copyright (c) 2015, Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
# s

#!/usr/bin/env python

import os
import constants

def generate(target, verbose, run):
    os.chdir(target)

    # Here we create a folder for each source or header file
    if os.path.exists("GCOVS/") and run:
        command = "rm -r GCOVS/"
        os.system(command)

    if run:
        recursive(target, os.path.join(target, "GCOVS"), target, verbose)


def recursive(target, dest, build_path, verbose):
    """
    now I will change working directory to
    PHP's Zend folder
    """
    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    # print os.getcwd()
    for item in dir_ls:
        if item.endswith(".c") or item.endswith(".cpp"):
            command = "mkdir -p " + os.path.join(dest, item)
            #	print command
            os.system(command)
        if item.endswith(".c") or item.endswith(".cpp"):
            # save the current path
            current_path = os.getcwd()

            # go to build path
            os.chdir(build_path)
            gcov_command = "gcov -bcu -o " + current_path + "/" \
                           + constants.Constants.IR.get_rule("Config.LIBS") \
                           + " " + os.path.join(current_path, item)
            if not verbose:
                gcov_command += " &> /dev/null"

            os.system(gcov_command)
            move_command = " mv *.gcov " + os.path.join(dest, item)

            if not verbose:
                move_command += " &> /dev/null"

            os.system(move_command)

            # go back to current path
            os.chdir(current_path)

        if os.path.isdir(item) and "GCOVS" not in item:
            recursive(item, os.path.join(dest, item), build_path, verbose)
    os.chdir(old_path)

# generate(sys.argv[1])
