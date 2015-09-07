__author__ = 'Gabriel-Cosmin SAMOILA'

import ini
import blacklist

"""
Class where we use all constants used in this tool
"""
class Constants:
    def __init__(self):
        pass

    """ types of tags """
    EXPECTED = "EXPECTED"
    UNEXPECTED = "UNEXPECTED"
    NONE = "NONE"

    """ types of predictions """
    OVERFLOW = "OVERFLOW"
    WRONG = "WRONG"
    MISSING = "MISSING"
    CORRECT = "CORRECT"

    IF = "IF"
    WHILE = "WHILE"
    FOR = "FOR"
    UNKNOWN = "UNKNOWN"
    WEIRD = "WEIRD"
    PATH_TO_SOURCES = "/home/GabrielCSMO/"

    BLACKLIST = []
    INI_MAP = {}
    INI_KEYS = ["Makefile.RULE", "Config.BLACKLIST", "Config.COMMAND", "Environment.WORKING_FOLDER"]
    #   you can add here default ini path as a string if you are lazy and don't want
    # to send path as -i param to main
    DEFAULT_INI_FILE = ""
    IR = None
    BR = None
