__author__ = 'Gabriel-Cosmin SAMOILA'

import ini
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
DEFAULT_INI_FILE = "php_data.ini"
LIBS_PATH = ".libs/"

IR = ini.IniReader(DEFAULT_INI_FILE)
IR.read()

