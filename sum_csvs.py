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

filename1 = ""
filename2 = ""
file1 = None
file2 = None
hmap = {}


def main(argv=sys.argv):
    global filename1, filename2
    if len(sys.argv) != 3:
        print "You must give filename parameter"
        exit()

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    print filename1
    print filename2


class Merge():
    def __init__(self, fname1, fname2):
        self.map = {}
        self.filename1 = fname1
        self.filename2 = fname2
        self.file1 = None
        self.file2 = None

    def open_files(self):
        try:
            self.file1 = open(self.filename1, 'r')
            self.file2 = open(self.filename2, 'r')
        except:
            print "error while opening the files"
            raise

    def start(self):
        content1 = self.file1.read().splitlines()
        content2 = self.file2.read().splitlines()
        print content1[1]
        print content2[1]
        for i in range(len(content1)):
            if i == 0:
                i += 1

            lista = content1[i].split(", ")
            line = lista[0]
            proc = float(lista[1])
            b0 = int(lista[2])
            b1 = int(lista[3])
            exp = int(lista[4])
            mod_line = [proc, b0, b1, exp]
            self.map[line] = mod_line

        print len(self.map)

        for i in range(len(content2)):
            if i == 0:
                i += 1
            lista = content2[i].split(", ")
            line = lista[0]
            proc = float(lista[1])
            b0 = int(lista[2])
            b1 = int(lista[3])
            exp = int(lista[4])
            mod_line = [proc, b0, b1, exp]

            if line not in self.map:
                self.map[line] = mod_line
            # print line
            else:
                self.map[line][1] += mod_line[1]
                self.map[line][2] += mod_line[2]
                total = self.map[line][1] + self.map[line][2]
                percent = self.map[line][1] * 100.0 / total
                self.map[line][0] = round(percent , 2)

        od = collections.OrderedDict(self.map.items())
        for i in od.items():
            print i

        def getMap(self):
            return self.map


if __name__ == "__main__":
    main()
    m = Merge(filename1, filename2)
    m.open_files()
    m.start()
