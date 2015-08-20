__author__ = 'Gabriel-Cosmin SAMOILA'

import ini
import blacklist
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


BLACKLIST = []
INI_MAP = {}
INI_KEYS = ["Makefile.RULE", "Config.BLACKLIST", "Config.COMMAND", "Config.LIBS"]
#   you can add here default ini path as a string if you are lazy and don't want
# to send path as -i param to main
DEFAULT_INI_FILE = "branch_hints.ini"

IR = ini.IniReader(DEFAULT_INI_FILE)
IR.read()

BR = blacklist.BlacklistReader(IR.getRule("Config.BLACKLIST"))
BR.read()
