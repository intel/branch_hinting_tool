#!/usr/bin/env python
__author__ = 'Gabriel-Cosmin Samoila'
import os
import sys
import constants
import main
"""
This class is used to read .ini file configuration and store
all rules in Constants class
"""


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

    def read(self):
        # self.initMap()
        content = self.file.readlines()
        for line in content:
            # a new section begins
            clean_line = line.rstrip("\t \r").strip("\t ")
            if clean_line.startswith("["):
                # print "New Section:" + clean_line[1:-2]
                self.currentSection = clean_line[1:-2]
            elif clean_line.startswith("#"):
                """
                do nothing , it is a comment
                """
            elif "=" in clean_line:
                lista = clean_line.split("=")
                key = self.currentSection + "." \
                      + lista[0].rstrip("\t \r\n").strip("\t ")
                value = lista[1].rstrip("\t \r\n").strip("\t ")
                self.map[key] = value

        for key in self.map:
            constants.Constants.INI_MAP[key] = self.map[key]

        for item in constants.Constants.INI_KEYS:
            if item not in self.map:
                raise EnvironmentError(
                    item + ' is not properly set in '
                    + constants.Constants.DEFAULT_INI_FILE + ' file')

        if "Config.LIBS" in self.map:
            constants.Constants.LIBS_PATH = self.map["Config.LIBS"]

    def get_rule(self, name):
        if name in self.map:
            return self.map[name]
        else:
            return None

    def to_string(self):
        result=""
        for key in self.map:
            result = result + key + "=" + self.map[key] + ","
