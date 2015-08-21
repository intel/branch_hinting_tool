#!/usr/bin/env python
__author__ = 'Gabriel-Cosmin Samoila'
import os
import sys
import constants
import main
class IniReader():

    def __init__(self, filen):
        self.filename = filen
        self.map = {}
        self.currentSection = ""
        try:
            self.file = open(self.filename, 'r')
        except:
            print "parse_time.csv: error opening file for write\n"
            raise
    """
    def initMap(self):
        self.map["Makefile.RULE"] = "make"
        self.map["Makefile.THREADS"] = "8"
        self.map["Makefile.CLEAN"] = "make clean"
        self.map["Makefile.EXIST"] = "YES"
        self.map["Config.BLACKLIST"] = "blacklist.cfg"
        self.map["Config.TARGET"] = " /var/www/html/wpxy/index.php"
        self.map["Config.BINARY"] = "./sapi/cgi/php-cgi -T1000 "
        self.map["Config.LIBS"] = ".libs/"
    """
    def read(self):
        #self.initMap()
        content = self.file.readlines()
        for line in content:
            # a new section begins
            clean_line = line.rstrip("\t \r").strip("\t ")
            if clean_line.startswith("[") :
                #print "New Section:" + clean_line[1:-2]
                self.currentSection = clean_line[1:-2]
            elif clean_line.startswith("#"):
                """
                do nothing , it is a comment
                """
            elif "=" in clean_line:
                lista = clean_line.split("=")
                key = self.currentSection + "." + lista[0].rstrip("\t \r\n").strip("\t ")
                value =lista[1].rstrip("\t \r\n").strip("\t ")
                self.map[key] = value
                #print key + " - " + value
        for key in self.map:
            constants.Constants.INI_MAP[key] = self.map[key]
        for item in constants.Constants.INI_KEYS:
            if item not in self.map:
                raise EnvironmentError(item + ' is not properly set in ' + constants.Constants.DEFAULT_INI_FILE + ' file')
        if "Config.LIBS" in self.map:
            #print "HEIL: " + self.map["Config.LIBS"]
            constants.Constants.LIBS_PATH = self.map["Config.LIBS"]

    def getRule(self, name):
        if name in self.map:
            return self.map[name]
        else:
            return None

    def toString(self):
        for key in self.map:
            print key + "=" + self.map[key]

"""
def main():
    IR = IniReader(sys.argv[1])
    IR.read()
    IR.toString()

if __name__ == '__main__':
    main()
"""