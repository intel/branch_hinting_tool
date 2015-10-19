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
import sys

import constants

sys.path.insert(0, 'branch_tagger')
import apply_on_folder

original_path = "Zend"
save_path = "Zend_modified"
FILENAME = ""


def main(argv=sys.argv):
    global original_path, save_path
    if len(sys.argv) != 3:
        print "Change script vars or call this with parameters"
    else:
        original_path = sys.argv[1]
        save_path = sys.argv[2]



def start(target):
    apply_on_folder.apply(target, constants.Constants.BLACKLIST)
