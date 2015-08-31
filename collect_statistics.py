#!/usr/bin/env python

"""
DOES THE SUM OF 2 CSV FILES(ON 3RD AND 4TH
COLUMN BASED ON  EQUALITY ON 1ST COLUMN)
"""

import os
import constants

FILENAME = ""
FILENAME_OUT = ""
file1 = None
hmap = {}
EXPECTED_LIMIT = 40  # limit for branch taken
UNEXPECTED_LIMIT = 60  # limit for branch not taken

"""
Class used to store each condition reported by gcov.
"""


class Condition():
    def __init__(self, filename, line, tpe, br0, br1, pr):
        self.filename = filename
        self.line = line
        self.type = tpe
        self.branch0 = br0
        self.branch1 = br1
        self.proc = pr
        self.state = constants.Constants.MISSING

    def to_string(self):
        s = self.filename + " "
        s += "line " + str(self.line) + " :\n"
        if self.type == 0:
            s += "\tType : EXPECTED\n"
        else:
            s += "\tType : UNEXPECTED\n"
        s += "\tTimes Taken : \n\t\tBranch 0: " \
             + str(self.branch0) + "\n\t\tBranch 1: " \
             + str(self.branch1) + "\n"
        s += "\tPercent times taken: " \
             + str(self.proc) + "%\n"
        return s


"""
Class used to collect all Conditions from a gcov file.
Tags each condition as wrong / right hinted
"""


class Collector():
    def __init__(self):
        self.map = {}
        self.file = None
        self.wrongExpected = []
        self.wrongUnexpected = []
        self.rightPredicted = []

    def print_wrong_expected(self):
        print "-=====- WRONG EXPECTED -=====-\n"
        for c in self.wrongExpected:
            print c.to_string()

    def print_wrong_unexpected(self):
        print "-=====- WRONG UNEXPECTED -=====-\n"
        for c in self.wrongUnexpected:
            print c.to_string()

    def print_right_predicted(self):
        print "-=====- RIGHT PREDICTIONS -=====-\n"
        for c in self.rightPredicted:
            print c.to_string()

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
            line = int(lista[0])
            proc = int(float(lista[1]))
            b0 = int(lista[2])
            b1 = int(lista[3])
            exp = lista[4]
            num_br = int(lista[5])
            key = fname + ", " + str(line)
            if key in self.map:
                b0 += self.map[key][5]
                b1 += self.map[key][6]
                proc = round(b0 * 100 / (b0 + b1), 0)
            # if "GCOVS" in path:
            #	print path
            path = path.replace("/GCOVS/", "/")
            if num_br > 2:
                mod_line = [constants.Constants.OVERFLOW,
                            exp,
                            constants.Constants.NONE,
                            (b0 + b1),
                            proc,
                            b0,
                            b1,
                            lista[5],
                            lista[6],
                            lista[7],
                            path]
            elif exp == constants.Constants.EXPECTED \
                    and proc < EXPECTED_LIMIT:
                self.wrongExpected.append(Condition(filename,
                                                    line,
                                                    exp,
                                                    b0,
                                                    b1,
                                                    proc))
                mod_line = [constants.Constants.WRONG,
                            exp,
                            constants.Constants.UNEXPECTED,
                            (b0 + b1),
                            proc,
                            b0,
                            b1,
                            lista[5],
                            lista[6],
                            lista[7],
                            path]
            elif exp == constants.Constants.UNEXPECTED \
                    and proc > UNEXPECTED_LIMIT:
                self.wrongUnexpected.append(Condition(filename,
                                                      line,
                                                      exp,
                                                      b0,
                                                      b1,
                                                      proc))
                mod_line = [constants.Constants.WRONG,
                            exp,
                            constants.Constants.EXPECTED,
                            (b0 + b1),
                            proc,
                            b0,
                            b1,
                            lista[5],
                            lista[6],
                            lista[7],
                            path]
            elif (exp == constants.Constants.EXPECTED
                  and proc > EXPECTED_LIMIT) \
                    or (exp == constants.Constants.UNEXPECTED
                        and proc < UNEXPECTED_LIMIT):
                self.rightPredicted.append(Condition(filename,
                                                     line,
                                                     exp,
                                                     b0,
                                                     b1,
                                                     proc))
                mod_line = [constants.Constants.CORRECT,
                            exp,
                            exp,
                            (b0 + b1),
                            proc,
                            b0,
                            b1,
                            lista[5],
                            lista[6],
                            lista[7],
                            path]
            else:
                if proc < (UNEXPECTED_LIMIT + EXPECTED_LIMIT) / 2:
                    mod_line = [constants.Constants.MISSING,
                                exp,
                                constants.Constants.UNEXPECTED,
                                (b0 + b1),
                                proc,
                                b0,
                                b1,
                                lista[5],
                                lista[6],
                                lista[7],
                                path]
                else:
                    mod_line = [constants.Constants.MISSING,
                                exp,
                                constants.Constants.EXPECTED,
                                (b0 + b1),
                                proc,
                                b0,
                                b1,
                                lista[5],
                                lista[6],
                                lista[7],
                                path]

            self.map[key] = mod_line

    def write_output(self):

        for key in self.map:
            s = str(key[0]) + " / Line " + str(key[0]) + ": " + str(self.map[key][0]) + "\n"
            if self.map[key][0] == constants.Constants.WRONG \
                    or self.map[key][0] == constants.Constants.MISSING:
                s += "Expected Hint: " + self.map[key][2] + "(Taken" \
                     + str(self.map[key][4]) \
                     + "%) instead of " + self.map[key][1] + "\n"
            elif self.map[key][0] == constants.Constants.CORRECT:
                s += "Current Hint: " + self.map[key][1] + "\n"
            s += "Total: " + str(self.map[key][3]) \
                 + " / Taken: " + str(self.map[key][5]) \
                 + "(" + str(self.map[key][4]) \
                 + "%) / Not Taken: " + str(self.map[key][6]) \
                 + " (" + str(100 - self.map[key][4]) + "%)\n\n"
            # ofile.write(s)

    def write_csv(self, FILENAME):
        """
        Writes all the results saved in map attribute in addFile() method
        in a csv format
        """
        print "HEIL: " + FILENAME
        try:
            wfile = open(FILENAME, 'w')
        except:
            print FILENAME + " - Write to file: error opening file for write\n"
            raise
        s = "PATH, FILENAME, LINE, STATE, CURRENT HINT, EXPECTED HINT," \
            + " TOTAL #, TAKEN % , TAKEN, NOT TAKEN, NUM_BRANCHES, BRANCH TYPE, LINE OF CODE\n"
        wfile.write(s)

        for key in self.map:
            s = self.map[key][10] + ", " \
                + str(key) + ", " \
                + self.map[key][0] + ", " \
                + str(self.map[key][1]) + ", " \
                + str(self.map[key][2]) + ", " \
                + str(self.map[key][3]) + ", " \
                + str(self.map[key][4]) + ", " \
                + str(self.map[key][5]) + ", " \
                + str(self.map[key][6]) + ", " \
                + str(self.map[key][7]) + ", " \
                + str(self.map[key][8]) + ", " \
                + str(self.map[key][9]) + "\n"
            wfile.write(s)

        def getMap(self):
            return self.map


cstat = Collector()


def apply_on_folder(target):
    """
    Adds all files in a folder and it's subfolders
    """
    global cstat
    old_path = os.getcwd()
    os.chdir(target)
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):
            apply_on_folder(target + "/" + item)
        elif item.endswith(".c.csv") or item.endswith(".h.csv"):
            cstat.add_file(old_path, item)

    os.chdir(old_path)


def collect(target):
    apply_on_folder(target)
    cstat.write_csv(target + "/stats.csv")
