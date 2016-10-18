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

    def __init__(self, filename, line, tpe, br0, br1, pr):
        self.filename = filename
        self.line = line
        self.type = tpe
        self.branch0 = br0
        self.branch1 = br1
        self.proc = pr
        self.state = constants.Constants.MISSING

    def to_string(self):
        ret = self.filename + " "
        ret += "line " + str(self.line) + " :\n"
        if self.type == 0:
            ret += "\tType : EXPECTED\n"
        else:
            ret += "\tType : UNEXPECTED\n"
        ret += "\tTimes Taken : \n\t\tBranch 0: " \
             + str(self.branch0) + "\n\t\tBranch 1: " \
             + str(self.branch1) + "\n"
        ret += "\tPercent times taken: " \
             + str(self.proc) + "%\n"
        return ret


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
            print cond.to_string()

    def print_wrong_unexpected(self):
        print "-=====- WRONG UNEXPECTED -=====-\n"
        for cond in self.wrong_unexpected:
            print cond.to_string()

    def print_right_predicted(self):
        print "-=====- RIGHT PREDICTIONS -=====-\n"
        for cond in self.right_predicted:
            print cond.to_string()

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
            proc = int(float(lista[1]))
            branch0 = int(lista[2])
            branch1 = int(lista[3])
            exp = lista[4]
            num_br = int(lista[5])
            original_line_no = lista[7].strip().rstrip()
            if original_line_no == "0":
                original_line_no = ' '
            key = fname + ", " + str(line)
            if key in self.map:
                branch0 += self.map[key][5]
                branch1 += self.map[key][6]
                proc = round(branch0 * 100 / (branch0 + branch1), 0)
            # if "GCOVS" in path:
            #	print path
            path = path.replace("/GCOVS/", "/")
            if num_br > 2:
                mod_line = [constants.Constants.OVERFLOW,
                            exp,
                            constants.Constants.NONE,
                            (branch0 + branch1),
                            proc,
                            branch0,
                            branch1,
                            lista[5],
                            lista[6],
                            lista[8],
                            path,
                            original_line_no]
            elif exp == constants.Constants.EXPECTED \
                    and proc < EXPECTED_LIMIT:
                self.wrong_expected.append(Condition(filename,
                                                     line,
                                                     exp,
                                                     branch0,
                                                     branch1,
                                                     proc))
                if proc <= UNEXPECTED_LIMIT:
                    mod_line = [constants.Constants.WRONG,
                                exp,
                                constants.Constants.UNEXPECTED,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]
                else:
                    mod_line = [constants.Constants.CORRECT,
                                exp,
                                constants.Constants.NONE,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]

            elif exp == constants.Constants.UNEXPECTED \
                    and proc > UNEXPECTED_LIMIT:
                self.wrong_unexpected.append(Condition(filename,
                                                       line,
                                                       exp,
                                                       branch0,
                                                       branch1,
                                                       proc))
                if proc > EXPECTED_LIMIT:
                    mod_line = [constants.Constants.WRONG,
                                exp,
                                constants.Constants.EXPECTED,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]
                else:
                    mod_line = [constants.Constants.CORRECT,
                                exp,
                                constants.Constants.NONE,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]

            elif (exp == constants.Constants.EXPECTED
                  and proc > EXPECTED_LIMIT) \
                    or (exp == constants.Constants.UNEXPECTED
                        and proc < UNEXPECTED_LIMIT):
                self.right_predicted.append(Condition(filename,
                                                      line,
                                                      exp,
                                                      branch0,
                                                      branch1,
                                                      proc))
                mod_line = [constants.Constants.CORRECT,
                            exp,
                            exp,
                            (branch0 + branch1),
                            proc,
                            branch0,
                            branch1,
                            lista[5],
                            lista[6],
                            lista[8],
                            path,
                            original_line_no]

            elif exp == constants.Constants.NONE \
                    and proc < EXPECTED_LIMIT \
                    and proc > UNEXPECTED_LIMIT:
                mod_line = [constants.Constants.CORRECT,
                            exp,
                            exp,
                            (branch0 + branch1),
                            proc,
                            branch0,
                            branch1,
                            lista[5],
                            lista[6],
                            lista[8],
                            path,
                            original_line_no]
            else:
                if proc < UNEXPECTED_LIMIT:
                    mod_line = [constants.Constants.MISSING,
                                exp,
                                constants.Constants.UNEXPECTED,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]
                else:
                    mod_line = [constants.Constants.MISSING,
                                exp,
                                constants.Constants.EXPECTED,
                                (branch0 + branch1),
                                proc,
                                branch0,
                                branch1,
                                lista[5],
                                lista[6],
                                lista[8],
                                path,
                                original_line_no]

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
            wfile.write(self.map[key][10] + ", " \
                        + str(key) + ", " \
                        + self.map[key][11] + ", " \
                        + self.map[key][0] + ", " \
                        + str(self.map[key][1]) + ", " \
                        + str(self.map[key][2]) + ", " \
                        + str(self.map[key][3]) + ", " \
                        + str(self.map[key][4]) + ", " \
                        + str(self.map[key][5]) + ", " \
                        + str(self.map[key][6]) + ", " \
                        + str(self.map[key][7]) + ", " \
                        + str(self.map[key][8]) + ", " \
                        + str(self.map[key][9]).split(",")[0] + "\n")


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
        elif item.endswith(".c.csv") or item.endswith(".h.csv"):
            cstat.add_file(old_path, item)

    os.chdir(old_path)


def collect(target):
    cstat = Collector()
    apply_on_folder(target, cstat)
    cstat.write_csv(target + "/stats.csv")
