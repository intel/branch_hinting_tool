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

class Merge(object):
    """
    This class is used for merging the results stored in
    all .csv files. If same line from same file is encountered
    more than once, a sum line will be created where:
    sum_branch0 = branch0' + branch0''
    sum_branch1 = branch1' + branch1''
    taken% = sum_branch0 + sum_branch1 / sum_branch0 / 100.0
    All results are saved in class map attribute.
    """

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
            branch0 = int(lista[2])
            branch1 = int(lista[3])
            mod_line = [
                proc, branch0, branch1, lista[4], lista[5], lista[6], lista[7]]

            if line not in self.map:
                self.map[line] = mod_line
            else:
                self.map[line][1] += mod_line[1]
                self.map[line][2] += mod_line[2]
                total = self.map[line][1] + self.map[line][2]
                percent = self.map[line][1] * 100.0 / total
                self.map[line][0] = round(percent, 2)

    def get_map(self):
        return self.map

    def write_to_file(self, filename):
        print filename + "\n"
        wfile = None
        try:
            wfile = open(filename, 'w')
        except:
            raise SystemError(filename + ": error opening file\n")
        wfile.write(
            "line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n")

        for key in self.map:
            # print str(key) + " - " + str(self.map[key])
            line = str(key) + ", " + str(self.map[key][0]) \
                + ", " + str(self.map[key][1]) \
                + ", " + str(self.map[key][2]) \
                + ", " + str(self.map[key][3]) \
                + ", " + str(self.map[key][4]) \
                + ", " + str(self.map[key][5]) \
                + ", " + str(self.map[key][6]) + "\n"
            wfile.write(line)
