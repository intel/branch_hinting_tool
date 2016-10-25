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
import constants
import re

FILENAME = ""

def get_line_no(line):
    regex = re.compile(r"[*][0-9]+[:][ ]")
    match = regex.search(line)
    if match is not None:
        index_star = match.start()
        index_points = match.end()
        return line[index_star + 1:index_points - 2]
    return "0"


def apply_on_folder(target):

    old_path = os.getcwd()
    os.chdir(target)
    # print os.getcwd()
    dir_ls = os.listdir(".")
    for item in dir_ls:
        if os.path.isdir(item):
            apply_on_folder(target + "/" + item)
        elif item.endswith(".gcov"):
            generate(item)
    os.chdir(old_path)


def generate(fname):
    global FILENAME
    if len(fname) <= 0 or fname == None:
        print "You must give filename parameter"
        exit()

    FILENAME = fname
    csv_output = fname[:-5] + ".csv"
    raw_output = fname[:-5] + ".output"

    parser = Parser(fname)
    parser.start()

    # We have all the conditions in text in parser.conds list
    conds = parser.conditii

    # print_conds(parser.conditii)

    filtru = Filter(conds)
    filtru.remove_non_branch()
    filtru.remove_call()
    filtru.remove_never_executed()
    filtru.compute()

    Classifier(filtru.interesting_conds).classify_expected()

    log = Logger(filtru.interesting_conds,
                 filtru.only_never_executed, csv_output, raw_output)
    log.create_log_files()
    log.start()

class Branch(object):
    """
    branch object:
    name (eg. branch 1, unconditional 2 etc.)
    number - branch number parsed from name
    """

    def __init__(self, name, number, prob):
        self.name = name
        self.number = number
        self.probability = prob
        self.times_executed = 0

    def set_name(self, nume):
        self.name = nume

    def get_name(self):
        return self.name

    def get_probability(self):
        return self.probability

    def get_times_executed(self):
        return self.times_executed

    def extract_times_executed(self):
        lista = self.name.split("taken")
        self.set_name(lista[0].strip())
        self.times_executed = int(lista[1].strip().split(" ")[0])

        # here we extract the number of each branch
        alls = lista[0].split(" ")
        self.number = alls[len(alls) - 2]
        # print int(timesExec[0])

    def compute_probability(self, total):
        # print str(self.timesExecuted) + " -- " + str(nr)
        if "unconditional" not in self.name:
            self.probability = self.times_executed * 100.0 / total
        else:
            self.probability = 0.0


class Condition(object):
    def __init__(self, test, line):
        self.test = test
        self.line = line
        self.branches = []
        self.sum_branches = 0
        self.type = constants.Constants.UNKNOWN
        self.multi_cond = 0
        self.num_branches = 0
        self.expected = 2  # 0 - EXPECTED ; 1 - UNEXPECTED ; 2 - UNKNOWN

    def copy_condition(self, cond):
        self.test = cond.test
        self.line = cond.line
        self.branches = cond.branches

    def set_test(self, test):
        self.test = test

    def set_multicond(self):
        self.multi_cond = 1

    def reset_multicond(self):
        self.multi_cond = 0

    def set_line(self, lineno):
        self.line = lineno

    def get_branches(self):
        return self.branches

    def add_branch(self, name, number, prob):
        self.branches.append(Branch(name, number, prob))

    def get_test(self):
        return self.test

    def compute_sum_branches(self):
        for branch in self.branches:
            if "unconditional" not in branch.get_name():
                self.num_branches += 1
                self.sum_branches += branch.get_times_executed()

    def establish_type(self):
        if "if branch" in self.test:
            self.type = constants.Constants.IF
        elif "while branch" in self.test:
            self.type = constants.Constants.WHILE
        elif "for branch" in self.test:
            self.type = constants.Constants.FOR
        elif "?" in self.test:
            # conditional expression - might have some issues on C++ code
            self.type = constants.Constants.IF
        elif "weird condition" in self.test:
            self.type = constants.Constants.WEIRD

    def remove_branch(self, branch):
        self.branches.remove(branch)

    def get_branches_times_executed(self):
        lista = []
        for branch in self.branches:
            if "unconditional" not in branch.get_name():
                lista.append(branch.get_times_executed())
        return lista

    def to_string(self):

        filen = FILENAME.split("/")
        source_file = filen[len(filen) - 1][:-5]
        ret = "\n" + source_file + "(line " + str(self.line) +\
            "):\n\tCondition: " + self.test +\
            "\n\tType: " + self.type +\
            "\n\t#Branches: " + str(self.num_branches) +\
            "\n\tMulticond: " + str(self.multi_cond) +\
            "\n\tExpected: " + str(self.expected) +\
            "\n\tBranches:"
        for branch in self.branches:
            ret += "\n\t\t" + str(branch.number) + ": " +branch.name + " - " \
                + str(round(branch.probability, 2)) + "% (" \
                + str(branch.get_times_executed()) + " times executed)"

        return ret

    def print_condition(self):
        filen = FILENAME.split("/")
        source_file = filen[len(filen) - 1][:-5]
        print "\n" + source_file + "(line " \
            + str(self.line) + "):\n\tCondition: " + self.test
        print "\tType: " + self.type
        print "\t#Branches: " + str(self.num_branches)
        print "\tMulticond: " + str(self.multi_cond)
        print "\tBranches:"
        for branch in self.branches:
            #print(" %i : %s - %.2f (%i times executed)")
            print "\t\t" + str(branch.number) + ": " +branch.name + " - " \
                + str(round(branch.probability, 2)) + "% (" \
                + str(branch.get_times_executed()) + " times executed)"

    def get_sum_branches(self):
        return self.sum_branches

    def reset(self):
        self.test = ""
        self.line = 0
        self.branches = []


class Parser(object):

    def __init__(self, path):
        self.path = path
        self.conditii = []
        self.sharedcond = Condition("", 0)
        # print "A parser for file " + self.path + " was created!"

    def start(self):
        # print "Started to parse gcov file..."

        with open(self.path) as lines:
            content = lines.read().splitlines()

        prev_ubc = False
        current_ubc = content[0].startswith("unconditional") or \
                      content[0].startswith("branch") or \
                      content[0].startswith("call")
        for i in range(len(content) - 1):
            next_ubc = content[i + 1].startswith("unconditional") or \
                       content[i + 1].startswith("branch") or \
                       content[i + 1].startswith("call")
            if current_ubc and not prev_ubc:
                # print "Test line "+str(i)+":\n"

                # Split the line to find out the line number where the
                # branch/call occurs
                lista = content[i - 1].split(":")
                # print lista
                lineno = lista[1].strip().rstrip()
                test = lista[2].strip().rstrip()
                if len(lista) > 3:
                    test += (":" + lista[3])
                # print test
                self.sharedcond.set_test(test)
                self.sharedcond.set_line(lineno)

                # print content[i]
                self.sharedcond.add_branch(content[i], 0, 0)

                if not next_ubc:
                    cond = Condition("", 0)
                    cond.copy_condition(self.sharedcond)
                    self.conditii.append(cond)
                    self.sharedcond.reset()
                    # print "End test\n\n"

            elif current_ubc and next_ubc:
                self.sharedcond.add_branch(content[i], 0, 0)
                # print content[i]

            elif current_ubc and not next_ubc:
                # print content[i]
                self.sharedcond.add_branch(content[i], 0, 0)

                cond = Condition("", 0)
                cond.copy_condition(self.sharedcond)
                self.conditii.append(cond)
                self.sharedcond.reset()
                # print "End test\n\n"

            prev_ubc = current_ubc
            current_ubc = next_ubc
        try:
            lines.close()
        except:
            print "Unexpected file.close() error: ", sys.exc_info()[0]
            raise


class Filter(object):
    """
    This class will filter the conditions eliminating
    all of those where information isn't needed for us or
    incomplete
    """

    def __init__(self, conds):
        # the list with unfiltered conditions
        self.conditions = conds
        # contains only conditions with at least 1 branch
        self.branch_conds = []

        # useful conditions
        self.interesting_conds = []

        # conditions with only never executed branches
        self.only_never_executed = []
        # print "Started to filter the conditions results..."

        # here we set conditions types (IF/WHERE/FOR)
        self.establish_conditions_type()

    def remove_non_branch(self):
        """
        add to branch_conds the subset of conditions that contains
        at least one branch
        """
        for cond in self.conditions:
            for branch in cond.branches:
                if "branch" in branch.get_name():
                    # print "got here"
                    self.branch_conds.append(cond)
                    break

    def remove_call(self):
        """
        remove the each "call" considered condition branch
        """
        for cond in self.branch_conds:
            partialbr = []
            for branch in cond.get_branches():
                text = branch.get_name()
                if text.startswith("call") == False \
                        and text.startswith("unconditional") == False:
                    partialbr.append(branch)
            cond.branches = partialbr

    def remove_never_executed(self):
        """
        separates the conditions that were never executed from
        those with times executed != 0
        """
        for cond in self.branch_conds:
            partialbr = []
            for branch in cond.get_branches():
                text = branch.get_name()
                if "never executed" not in text:
                    partialbr.append(branch)
            if len(partialbr) == 0:
                self.only_never_executed.append(cond)
            else:
                cond.branches = partialbr
                self.interesting_conds.append(cond)

    def compute(self):
        """
        extracts how many times each branch was executed
        and his execution probability for each condition
        """

        # makes the sum of all condition branches
        for cond in self.interesting_conds:
            for branch in cond.get_branches():
                branch.extract_times_executed()

            cond.compute_sum_branches()
            total = cond.get_sum_branches()
            # computes the probability for each branch of actual condition
            for branch in cond.get_branches():
                branch.compute_probability(total)

    def establish_conditions_type(self):
        """
        sets the type of each condition based on "if/while/for/?" and other
        keywords found in condition text
        """
        for cond in self.conditions:
            cond.establish_type()

    def establish_conditions_type_leveltwo(self):
        """
        reiterates through all conditions and detects multiple conditions
        TODO: detect using /*MULTICOND*/ flag

        Here we will retag the Unknown resulted from multiple if conds
        We will get through all conditions and see if one of them is
        ending or starting with	&& or ||
        """
        for i in range(len(self.conditions) - 1):
            current_cond = self.conditions[i]
            next_cond = self.conditions[i + 1]
            test_current_cond = current_cond.get_test()  # .strip().rstrip()
            test_next_cond = next_cond.get_test()  # .strip().rstrip()

            if current_cond.type != "UNKNOWN" and \
               next_cond.type == "UNKNOWN" and \
               (test_current_cond[-2:] in ["&&", "||"] or \
                test_next_cond[0:2] in ["&&", "||"]):

                next_cond.type = current_cond.type
                current_cond.set_multicond()
                next_cond.set_multicond()


class Classifier(object):
    """
    Conditions are classified by type or
    by Expectations and printed when it's needed
    """

    def __init__(self, conds):
        self.all_conds = conds
        self.if_conds = []
        self.while_conds = []
        self.for_conds = []
        self.unknown_conds = []
        self.macro_conds = []

    def classify_expected(self):
        for cond in self.all_conds:
            unlikely = constants.Constants.UNLIKELY
            likely = constants.Constants.LIKELY
            if unlikely and \
               any(word in cond.get_test() for word in unlikely):
                cond.expected = constants.Constants.UNEXPECTED
            elif likely and \
                 any(word in cond.get_test() for word in likely):
                cond.expected = constants.Constants.EXPECTED
            else:
                cond.expected = constants.Constants.NONE

    def classify_type(self):
        for cond in self.all_conds:
            if cond.type == constants.Constants.IF:
                self.if_conds.append(cond)
            elif cond.type == constants.Constants.WHILE:
                self.while_conds.append(cond)
            elif cond.type == constants.Constants.FOR:
                self.for_conds.append(cond)
            elif cond.type == "MACRO":
                self.macro_conds.append(cond)
            else:
                self.unknown_conds.append(cond)

    def print_cc(self):
        print "\n\n-=- IF _conditions -=-\n\n"
        print_conds(self.if_conds)
        print "\n\n-=- WHILE Conditions -=-\n\n"
        print_conds(self.while_conds)
        print "\n\n-=- FOR Conditions -=-\n\n"
        print_conds(self.for_conds)
        print "\n\n-=- MACRO Conditions -=-\n\n"
        print_conds(self.macro_conds)
        print "\n\n-=- Unknown Conditions -=-\n\n"
        print_conds(self.unknown_conds)


class Logger(object):
    """
    Output files are created and filled with information
    """

    def __init__(self, exec_conds, never_conds, filename_csv, filename_raw):
        self.exec_conditions = exec_conds
        self.never_conditions = never_conds
        self.csv_filename = filename_csv
        self.raw_filename = filename_raw
        self.csv_file = None
        self.raw_file = None

    def create_log_files(self):
        try:
            self.csv_file = open(self.csv_filename, 'w')
            self.raw_file = open(self.raw_filename, 'w')
        except:
            print "Unexpected file opening error:", sys.exc_info()[0]
            raise

    def start(self):
        # print str(len(self.exec_conditions))+ " - " +
        # str(len(self.never_conditions))
        self.write_csv()
        self.write_raw()

    def write_csv(self):
        """
        writes all the conditions with no more than 2 branches
        in the csv_file in the following format:
        tuples of: line #, taken, branch0_taken, branch1_taken,
                   expected, multiple
        where:	taken is % of how many times branch was taken
                expected: 0 - contition is EXPECTED to happend
                          1 - condition is UNEXPECTED to happend
                          2 - unknown expectation
        """
        try:
            self.csv_file.write(
                "line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n")
            for cond in self.exec_conditions:
                lista = cond.get_branches_times_executed()
                # print lista[0]
                probability = cond.get_branches()[0].get_probability()
                line = [cond.line,
                        None,
                        None,
                        None,
                        cond.expected,
                        cond.num_branches,
                        cond.type,
                        get_line_no(cond.test),
                        cond.test + "\n"]
                if "branch ||" in cond.test:
                    line[1] = round((100.0 - probability), 2)
                    line[2] = lista[1]
                    line[3] = lista[0]
                else:
                    line[1] = round((probability), 2)
                    line[2] = lista[0]
                    line[3] = lista[1]
                # print get_line_no(cond.test)
                self.csv_file.write(", ".join(str(item) for item in line))

        except:
            print "Unexpected file writing error"
            raise

        try:
            self.csv_file.close()
        except:
            print "Error on closing file"
            raise

        # print "Done writing in " + self.csv_filename + " ..."

    def write_raw(self):
        """ writes each condition in the raw_file in the following format
            Filename(line x):
            Condition: condition text
            Type: type of condition(IF,WHILE ...)
            #Branches: Number of branches in condition
            Multicond: 0 - not a part of a multiple condition
                       1 - a part of a multiple condition
            Expected: 0 - contition is EXPECTED to happend
                      1 - condition is UNEXPECTED to happend
                      2 - unknown expectation
        Branches:
            # : branch name - probability% (x times executed)
        """
        try:
            for cond in self.exec_conditions:
                out = cond.to_string()
                self.raw_file.write(out)

            self.raw_file.write("\n\n---- Never Executed ----\n\n")
            for cond in self.never_conditions:
                out = cond.to_string()
                self.raw_file.write(out)
        except:
            print "Unexpected file writing error:", sys.exc_info()[0]
            raise

        try:
            self.raw_file.close()
        except:
            print "Error on closing file"
            raise

        # print "Done writing in " + self.raw_filename + " ..."


def print_conds(conds):
    for cond in conds:
        # if cond.num_branches <= 2:
        cond.print_condition()


# if __name__ == "__main__" :
# applyOnFolder(sys.argv[1])
