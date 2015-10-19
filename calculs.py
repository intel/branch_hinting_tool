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

import sys
import os
import collections

hmap = {}

"""
    This class is used for merging the results stored in
all .csv files. If same line from same file is encountered
more than once, a sum line will be created where:
sum_branch0 = branch0' + branch0''
sum_branch1 = branch1' + branch1''
taken% = sum_branch0 + sum_branch1 / sum_branch0 / 100.0
All results are saved in class map attribute.
"""


class Merge():
    def __init__(self):
        self.file = None
        self.map = {}

    def add_file(self, filename):

        try:
            self.file = open(filename, 'r')
        except:
            print "error while opening the files"
            raise

        content = self.file.read().splitlines()

        for i in range(len(content)):
            if i == 0:
                continue
            lista = content[i].split(", ")
            line = lista[0]
            proc = float(lista[1])
            b0 = int(lista[2])
            b1 = int(lista[3])
            mod_line = [proc, b0, b1, lista[4], lista[5], lista[6], lista[7]]

            if line not in self.map:
                self.map[line] = mod_line
            else:
                self.map[line][1] += mod_line[1]
                self.map[line][2] += mod_line[2]
                sum = self.map[line][1] + self.map[line][2]
                percent = self.map[line][1] * 100.0 / sum
                self.map[line][0] = round(percent, 2)

    def get_map(self):
        return self.map

    def write_to_file(self, filename):
        print filename + "\n"
        wfile = None
        try:
            wfile = open(filename, 'w')
        except:
            raise SystemError(self.filename + ": error opening file\n")
        s = "line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n"
        wfile.write(s)

        for key in self.map:
            # print str(key) + " - " + str(self.map[key])
            s = str(key) + ", " + str(self.map[key][0]) \
                + ", " + str(self.map[key][1]) \
                + ", " + str(self.map[key][2]) \
                + ", " + str(self.map[key][3]) \
                + ", " + str(self.map[key][4]) \
                + ", " + str(self.map[key][5]) \
                + ", " + str(self.map[key][6]) + "\n"
            wfile.write(s)
