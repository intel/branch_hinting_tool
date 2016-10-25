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

"""
DOES THE SUM OF 2 CSV FILES(ON 3RD AND 4TH
COLUMN BASED ON  EQUALITY ON 1ST COLUMN)
"""

import os
import constants

# limit for branch taken
EXPECTED_LIMIT = constants.Constants.EXPECTED_LIMIT
# limit for branch not taken
UNEXPECTED_LIMIT = constants.Constants.UNEXPECTED_LIMIT

class Condition(object):
    """
    Class used to store each condition reported by gcov.
    """

    def __init__(self, filename, line, tpe, branch0, branch1, probability):
        self.filename = filename
        self.line = line
        self.type = "EXPECTED" if tpe == 0 else "UNEXPECTED"
        self.branch0 = branch0
        self.branch1 = branch1
        self.proc = probability
        self.state = constants.Constants.MISSING

    def __str__(self):
        ret = "%s line %s:\n\tType : %s\tTimes Taken : \n\t\t"
        ret += "Branch 0: %s\n\t\tBranch 1: %s\n\tPercent times taken: %s%%\n"
        args = (self.filename, self.line, self.type, self.branch0,
                self.branch1, self.proc)
        return ret % args


class Collector(object):
    """
    Class used to collect all Conditions from a gcov file.
    Tags each condition as wrong / right hinted
    """

    def __init__(self):
        self.map = {}
        self.file = None
        self.wrong_expected = []
        self.wrong_unexpected = []
        self.right_predicted = []

    def print_wrong_expected(self):
        print "-=====- WRONG EXPECTED -=====-\n"
        for cond in self.wrong_expected:
            print cond

    def print_wrong_unexpected(self):
        print "-=====- WRONG UNEXPECTED -=====-\n"
        for cond in self.wrong_unexpected:
            print cond

    def print_right_predicted(self):
        print "-=====- RIGHT PREDICTIONS -=====-\n"
        for cond in self.right_predicted:
            print cond

    def print_all(self):
        self.print_wrong_expected()
        self.print_wrong_unexpected()
        self.print_right_predicted()

    def add_file(self, path, filename):
        try:
            self.file = open(filename, 'r')
        except:
            print "error while opening the files"
            raise
        fname = filename[:-4]
        content = self.file.read().splitlines()
        for i in range(len(content)):
            if i == 0:
                continue
            lista = content[i].split(", ")
            # print lista

            line = int(lista[0])
            branch0 = int(lista[2])
            branch1 = int(lista[3])
            exp = lista[4]
            num_br = int(lista[5])
            original_line_no = lista[7].strip()
            if original_line_no == "0":
                original_line_no = ' '
            key = fname + ", " + str(line)
            if key in self.map:
                branch0 += self.map[key][5]
                branch1 += self.map[key][6]
                if branch0 + branch1 == 0:
                    proc = 0
                else: proc = round(branch0 * 100 / (branch0 + branch1), 0)
            else:
                proc = int(float(lista[1]))
            # if "GCOVS" in path:
            #	print path
            path = path.replace("/GCOVS/", "/")
            mod_line = [None,
                        exp,
                        None,
                        branch0 + branch1,
                        proc,
                        branch0,
                        branch1,
                        lista[5],
                        lista[6],
                        lista[8],
                        path,
                        original_line_no]
            condition = Condition(filename,
                                  line,
                                  exp,
                                  branch0,
                                  branch1,
                                  proc)
            if num_br > 2:
                mod_line[0] = constants.Constants.OVERFLOW
                mod_line[2] = constants.Constants.NONE
            elif exp == constants.Constants.EXPECTED \
                    and proc < EXPECTED_LIMIT:
                self.wrong_expected.append(condition)
                if proc <= UNEXPECTED_LIMIT:
                    mod_line[0] = constants.Constants.WRONG
                    mod_line[2] = constants.Constants.UNEXPECTED
                else:
                    mod_line[0] = constants.Constants.CORRECT
                    mod_line[2] = constants.Constants.NONE

            elif exp == constants.Constants.UNEXPECTED \
                    and proc > UNEXPECTED_LIMIT:
                self.wrong_unexpected.append(condition)
                if proc > EXPECTED_LIMIT:
                    mod_line[0] = constants.Constants.WRONG
                    mod_line[2] = constants.Constants.EXPECTED
                else:
                    mod_line[0] = constants.Constants.CORRECT
                    mod_line[2] = constants.Constants.NONE

            elif (exp == constants.Constants.EXPECTED
                  and proc > EXPECTED_LIMIT) \
                    or (exp == constants.Constants.UNEXPECTED
                        and proc < UNEXPECTED_LIMIT):
                self.right_predicted.append(condition)
                mod_line[0] = constants.Constants.CORRECT
                mod_line[2] = exp

            elif exp == constants.Constants.NONE \
                    and proc < EXPECTED_LIMIT \
                    and proc > UNEXPECTED_LIMIT:
                mod_line[0] = constants.Constants.CORRECT
                mod_line[2] = exp
            else:
                if proc < UNEXPECTED_LIMIT:
                    mod_line[0] = constants.Constants.MISSING
                    mod_line[2] = constants.Constants.UNEXPECTED
                else:
                    mod_line[0] = constants.Constants.MISSING
                    mod_line[2] = constants.Constants.EXPECTED

            self.map[key] = mod_line

    def write_csv(self, filename):
        """
        Writes all the results saved in map attribute in addFile() method
        in a csv format
        """
        print "Done. Writing results in " + filename
        try:
            wfile = open(filename, 'w')
        except:
            print filename + " - Write to file: error opening file for write\n"
            raise
        wfile.write(
            "PATH, FILENAME, LINE,ORIGINAL_LINE_NO, STATE, " + \
            "CURRENT HINT, EXPECTED HINT, TOTAL #, TAKEN % , TAKEN, " + \
            "NOT TAKEN, NUM_BRANCHES, BRANCH TYPE, LINE OF CODE\n")

        for key in self.map:
            value = self.map[key]
            line = [value[10], key, value[11]] + value[0:9] + [
                str(value[9]).split(',')[0]]
            wfile.write(", ".join([str(item) for item in line]) + "\n")


def apply_on_folder(target, cstat):
    """
    Adds all files in a folder and it's subfolders
    """
    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):
            apply_on_folder(target + "/" + item, cstat)
        elif item.endswith(".c.csv") or \
             item.endswith(".h.csv") or \
             item.endswith(".cpp.csv"):
            cstat.add_file(old_path, item)

    os.chdir(old_path)


def collect(target):
    cstat = Collector()
    apply_on_folder(target, cstat)
    cstat.write_csv(target + "/stats.csv")
