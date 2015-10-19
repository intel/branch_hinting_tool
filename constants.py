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
    EXPECTED_LIMIT = 50
    UNEXPECTED_LIMIT = 50
    LIKELY = None
    UNLIKELY = None
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
