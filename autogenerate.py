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
###########################################################################

#!/usr/bin/env python

import os
import sys
import argparse
import constants
import ini
import collect_statistics
# IR.toString()

OLD_opt_flag = "-O2"
NEW_opt_flag = "-O0"
OLD_prof_flag = "-fprofile-generate"
NEW_prof_flag = "--coverage"
CONT = ""
NUM_THREADS = 8
DEST = None
TARGET = "/var/www/html/wpxy/index.php"
PATH = "/home/GabrielCSMO/Documents"

parser = argparse.ArgumentParser(description="PHP engine auto build and run script")
parser.add_argument("--target", "-t", metavar='TARGET', type=str, nargs='?', help='php file')
parser.add_argument("--path", "-p", metavar='PATH', type=str, nargs='?', help='folder where php is located')
parser.add_argument('--destination', '-d', metavar='DEST', type=str, nargs='?',
                    help='html lcov destionation folder (if you pass this argument, lcov will be called')
parser.add_argument('--numthreads', '-n', metavar='NUM_THREADS', type=int, nargs='?',
                    help='number of threads used for build')
parser.add_argument('-r', action='store_true', help='redo initial config after collecting the results')
args = parser.parse_args()

if args.target != None:
    TARGET = args.target

if args.destination != None:
    DEST = args.destination

if args.path != None:
    PATH = args.path

if args.numthreads != None:
    NUM_THREADS = args.numthreads

if DEST != None:
    print "LCOV destination folder: " + DEST
    command = "rm -r " + DEST + "/lcov_results"
    os.system(command)
    print command

    command = "mkdir -p " + DEST + "/lcov_results/html"
    os.system(command)
    print command

print "Changind directory to " + PATH
os.chdir(PATH)

command = "sed \"s/" + OLD_opt_flag + "/" \
          + NEW_opt_flag + "/g\"" " \"Makefile\" > Makefile.copy"
os.system(command)
print command

os.system("cp Makefile.copy Makefile")

command = "sed \"s/" + OLD_prof_flag + "/" \
          + NEW_prof_flag + "/g\"" " \"Makefile\" > Makefile.copy"
os.system(command)
print command

os.system("cp Makefile.copy Makefile")
os.system("make clean")
print constants.Constants.IR.to_string()
command = constants.Constants.IR.get_rule("Makefile.RULE")  # +" &> /dev/null"
os.system(command)
print command

os.system("pwd")
command = constants.Constants.IR.get_rule("Config.COMMAND")  # + " &> /dev/null"
os.system(command)
print command

# print "Destination: "+DEST + "\nPATH: "+PATH
if DEST != None:
    command = "lcov --directory " + PATH + "/Zend/.libs/ " \
              + "--rc lcov_branch_coverage=1 --capture --o " \
              + DEST + "/lcov_results/results.lcov"
    os.system(command)
    print command

    command = "genhtml --branch-coverage -o " + DEST \
              + "/lcov_results/html " + DEST + "/lcov_results/results.lcov"
    os.system(command)
    print command

os.system("rm Makefile.copy")
