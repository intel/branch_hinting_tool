#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import os
import sys
import constants
import re

def get_line_no(line):
    regex = re.compile(r"[*][0-9]+[:][ ]")
    match = regex.search(line)
    if match is not None:
        index_star = match.start()
        index_points = match.end()
        return line[index_star + 1:index_points - 2]
    return '0'


def apply_on_folder(target):

    old_path = os.getcwd()
    os.chdir(target)

    # print os.getcwd()

    dir_ls = os.listdir('.')
    for item in dir_ls:
        if os.path.isdir(item):
            apply_on_folder(target + '/' + item)
        elif item.endswith('.gcov'):
            generate(item)
    os.chdir(old_path)


def generate(fname):

    if not fname or len(fname) <= 0:
        print 'You must give filename parameter'
        exit()

    filename = fname
    csv_output = fname[:-5] + '.csv'
    raw_output = fname[:-5] + '.output'

    parser = Parser(filename)
    parser.start()

    conds = parser.conditii

    # printConds(parser.conditii)

    filtru = Filter(conds)
    filtru.remove_non_branch()
    filtru.remove_call()
    filtru.remove_never_executed()
    filtru.compute()

    Classifier(filtru.interesting_conds).classify_expected()

    log = Logger(filtru.interesting_conds, filtru.only_never_executed,
                 csv_output, raw_output)
    log.create_log_files()
    log.start()


'''Branch object:
  name (eg. branch 1, unconditional 2 etc.)
  number - branch number parsed from name
'''
class Branch(object):
    def __init__(self,
                 name,
                 prob):
        self.name = name
        self.probability = prob
        self.times_executed = 0
        self.number = 0

    def set_name(self, nume):
        self.name = nume

    def get_name(self):
        return self.name

    def get_probability(self):
        return self.probability

    def get_times_executed(self):
        return self.times_executed

    def extract_times_executed(self):
        lista = self.name.split('taken')
        self.set_name(lista[0].strip())
        self.times_executed = int(lista[1].split()[0])
        self.number = lista[0].split()[-1]

    def compute_probability(self, total):
        if 'unconditional' not in self.name:
            self.probability = self.times_executed * 100.0 / total
        else:
            self.probability = 0.0


class Condition(object):
    def __init__(self, parser):
        self.parser = parser
        self.test = ''
        self.line = 0
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

    def add_branch(self,
                   name,
                   prob):
        self.branches.append(Branch(name, prob))

    def get_test(self):
        return self.test

    def compute_sum_branches(self):
        for branch in self.branches:
            if 'unconditional' not in branch.get_name():
                self.num_branches += 1
                self.sum_branches += branch.get_times_executed()

    def establish_type(self):
        if 'if branch' in self.test:
            self.type = constants.Constants.IF
        elif 'while branch' in self.test:
            self.type = constants.Constants.WHILE
        elif 'for branch' in self.test:
            self.type = constants.Constants.FOR
        elif '?' in self.test:
            # conditional expression - might have some issues on C++ code
            self.type = constants.Constants.IF
        elif 'weird condition' in self.test:
            self.type = constants.Constants.WEIRD

    def remove_branch(self, branch):
        self.branches.remove(branch)

    def get_branches_times_executed(self):
        lista = []
        for branch in self.branches:
            if 'unconditional' not in branch.get_name():
                lista.append(branch.get_times_executed())
        return lista

    def to_string(self):
        source_file = self.parser.path.split('/')[-1][:-5]
        branches = ['%s: %s - %s%% (%s times executed)' % (
            branch.number, branch.name, round(branch.probability, 2),
            branch.get_times_executed()) for branch in self.branches]
        if branches:
            branches = '\n\t\t' + branches

        line = ['%s(line %s):' % (source_file, self.line),
                'Condition: ' + self.test,
                'Type: ' % self.type,
                '#Branches: %s' % self.num_branches,
                'Multicond: %s' % self.multi_cond,
                'Expected: %s' % self.expected,
                'Branches: %s' % '\n\t\t'.join(branches)]
        return '\n' + "\n\t".join(line)

    def print_condition(self):
        source_file = self.parser.path.split('/')[-1][:-5]
        print '\n' + source_file + '(line ' + str(self.line) \
            + '):\n\tCondition: ' + self.test
        print '\tType: ' + self.type
        print '\t#Branches: ' + str(self.num_branches)
        print '\tMulticond: ' + str(self.multi_cond)
        print '\tBranches:'
        for branch in self.branches:
            print '\t\t' + str(branch.number) + ': ' + branch.name + ' - ' \
                + str(round(branch.probability, 2)) + '% (' \
                + str(branch.get_times_executed()) + ' times executed)'

    def get_sum_branches(self):
        return self.sum_branches

    def reset(self):
        self.test = ''
        self.line = 0
        self.branches = []


class Parser(object):

    def __init__(self, path):
        self.path = path
        self.conditii = []
        self.sharedcond = Condition(self)

        # print "A parser for file " + self.path + " was created!"

    def start(self):

        # print "Started to parse gcov file..."

        with open(self.path) as lines:
            content = lines.read().splitlines()

        for i in range(len(content) - 1):
            current_ubc = content[i].startswith('unconditional') \
                          or content[i].startswith('branch') \
                          or content[i].startswith('call')
            previous_ubc = content[i].startswith('unconditional') \
                           or content[i].startswith('branch') \
                           or content[i].startswith('call')
            next_ubc = content[i + 1].startswith('unconditional') \
                       or content[i + 1].startswith('branch') \
                       or content[i + 1].startswith('call')
            if current_ubc and not previous_ubc:

                # print "Test line "+str(i)+":\n"

                lista = content[i - 1].split(':')

                # print lista

                lineno = lista[1].strip().rstrip()
                test = lista[2].strip().rstrip()
                if len(lista) > 3:
                    test += ':' + lista[3]

                # print test

                self.sharedcond.set_test(test)
                self.sharedcond.set_line(lineno)

                # print content[i]

                self.sharedcond.add_branch(content[i], 0)

                if not next_ubc:
                    cond = Condition(self)
                    cond.copy_condition(self.sharedcond)
                    self.conditii.append(cond)
                    self.sharedcond.reset()
            elif current_ubc and next_ubc:

                    # print "End test\n\n"

                self.sharedcond.add_branch(content[i], 0)
            elif current_ubc and not next_ubc:

                self.sharedcond.add_branch(content[i], 0)

                cond = Condition(self)
                cond.copy_condition(self.sharedcond)
                self.conditii.append(cond)
                self.sharedcond.reset()

                # print "End test\n\n"

        try:
            lines.close()
        except:
            print 'Unexpected file.close() error: ', sys.exc_info()[0]
            raise


"""
This class will filter the conditions eliminating
all of those where information isn't needed for us or incomplete
"""
class Filter(object):

    def __init__(self, conds):
        # the list with unfiltered conditions
        self.conditions = conds
        # contains only conditions with at least 1 branch
        self.branch_conds = []

        # useful conditions
        self.interesting_conds = []
        # conditions with only never executed branches
        self.only_never_executed = []

        # here we set conditions types (IF/WHERE/FOR)
        self.establish_conditions_type()

    def remove_non_branch(self):
        for cond in self.conditions:
            for branch in cond.branches:
                if 'branch' in branch.get_name():
                    self.branch_conds.append(cond)
                    return

    def remove_call(self):
        for cond in self.branch_conds:
            partialbr = []
            for branch in cond.get_branches():
                text = branch.get_name()
                if not text.startswith('call') and \
                   not text.startswith('unconditional'):
                    partialbr.append(branch)
            cond.branches = partialbr

    def remove_never_executed(self):
        for cond in self.branch_conds:
            partialbr = []
            for branch in cond.get_branches():
                text = branch.get_name()
                if 'never executed' not in text:
                    partialbr.append(branch)
            if len(partialbr) == 0:
                self.only_never_executed.append(cond)
            else:
                cond.branches = partialbr
                self.interesting_conds.append(cond)

    def compute(self):
        """ makes the sum of all condition branches """

        for cond in self.interesting_conds:
            for branch in cond.get_branches():
                branch.extract_times_executed()

            cond.compute_sum_branches()
            total = cond.get_sum_branches()
            for branch in cond.get_branches():
                branch.compute_probability(total)

    def establish_conditions_type(self):
        for cond in self.conditions:
            cond.establish_type()

    """
    Here we will retag the Unknown resulted from multiple if conds
    We will get through all conditions and see if one of them is
    ending or starting with....&& or ||
    """
    def establish_conditions_type_leveltwo(self):

        for i in range(len(self.conditions) - 1):
            current_cond = self.conditions[i]
            next_cond = self.conditions[i + 1]
            test_current_cond = current_cond.get_test()  # .strip().rstrip()
            test_next_cond = next_cond.get_test()  # .strip().rstrip()

            if current_cond.type != 'UNKNOWN' and next_cond.type \
                == 'UNKNOWN' and (test_current_cond.endswith('&&')
                                  or test_current_cond.endswith('||')
                                  or test_next_cond.startswith('&&')
                                  or test_next_cond.startswith('||')):
                next_cond.type = current_cond.type
                current_cond.set_multicond()
                next_cond.set_multicond()



"""
Conditions are classified by type or
by Expectations and printed when it's needed
"""
class Classifier(object):

    def __init__(self, conds):
        self.all_conds = conds
        self.if_conds = []
        self.while_conds = []
        self.for_conds = []
        self.unknown_conds = []
        self.macro_conds = []

    def classify_expected(self):
        for cond in self.all_conds:
            if constants.Constants.UNLIKELY and \
                any(word in cond.get_test() \
                    for word in constants.Constants.UNLIKELY):
                cond.expected = constants.Constants.UNEXPECTED
            elif constants.Constants.LIKELY and \
                 any(word in cond.get_test() \
                     for word in constants.Constants.LIKELY):
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
            elif cond.type == 'MACRO':
                self.macro_conds.append(cond)
            else:
                self.unknown_conds.append(cond)

    def print_cc(self):
        print '''

-=- IF Conditions -=-

'''
        print_conds(self.if_conds)
        print '''

-=- WHILE Conditions -=-

'''
        print_conds(self.while_conds)
        print '''

-=- FOR Conditions -=-

'''
        print_conds(self.for_conds)
        print '''

-=- MACRO Conditions -=-

'''
        print_conds(self.macro_conds)
        print '''

-=- Unknown Conditions -=-

'''
        print_conds(self.unknown_conds)


"""Output files are created and filled with information"""
class Logger(object):

    def __init__(self,
                 exec_conds,
                 never_conds,
                 filenameCSV,
                 filenameRAW):
        self.exec_conditions = exec_conds
        self.never_conditions = never_conds
        self.csv_filename = filenameCSV
        self.raw_filename = filenameRAW
        self.csv_file = None
        self.raw_file = None

    def create_log_files(self):
        try:
            self.csv_file = open(self.csv_filename, 'w')
            self.raw_file = open(self.raw_filename, 'w')
        except:
            print 'Unexpected file opening error:', sys.exc_info()[0]
            raise

    def start(self):
        self.write_csv()
        self.write_raw()

    def write_csv(self):
        try:
            self.csv_file.write(
                'line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n')
            for cond in self.exec_conditions:
                lista = cond.get_branches_times_executed()

                # print lista[0]

                line = [cond.line,
                        round(100.0 -
                              cond.get_branches()[0].get_probability(), 2),
                        lista[1],
                        lista[0],
                        cond.expected,
                        cond.num_branches,
                        cond.type,
                        get_line_no(cond.test),
                        cond.test]
                if 'branch ||' not in cond.test:
                    line[2], line[3] = line[3], line[2]
                line = ", ".join([str(x) for x in line]) + '\n'
                self.csv_file.write(line)
        except:
            print 'Unexpected file writing error'
            raise

        try:
            self.csv_file.close()
        except:
            print 'Error on closing file'
            raise

    def write_raw(self):
        try:
            for cond in self.exec_conditions:
                out = cond.to_string()
                self.raw_file.write(out)

            self.raw_file.write('''

---- Never Executed ----

''')
            for cond in self.never_conditions:
                out = cond.to_string()
                self.raw_file.write(out)
        except:
            print 'Unexpected file writing error:', sys.exc_info()[0]
            raise

        try:
            self.raw_file.close()
        except:
            print 'Error on closing file'
            raise


def print_conds(conds):
    for cond in conds:
        cond.print_condition()

