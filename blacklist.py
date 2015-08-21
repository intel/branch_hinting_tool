#!/usr/bin/env python

import os
import sys
import constants

class BlacklistReader():

    def __init__(self, filen):
        self.filename = filen
        try:
            self.file = open(self.filename, 'r')
        except:
            print "parse_time.csv: error opening file for write\n"
            raise

    def read(self):
        content = self.file.readlines()
        for line in content:
            if len(line) > 3:
                constants.Constants.BLACKLIST.append(line.rstrip(" \n"))

    def toString(self):
        s = ""
        for file in constants.Constants.BLACKLIST:
            s += file
        return s

"""
def main():
    br = BlacklistReader(sys.argv[1])
    br.read()
    print br.toString()

if __name__ == "__main__":
    main()
"""