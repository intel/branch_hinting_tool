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

from global_var import GlobalVar
from apply_fsm_file import ApplyFSMFile


"""
 Performs tagging on a file given as argument, creates a string representing the tagged file
 and outputs it in a file given as argument.
"""


def tag(input, output):
    ApplyFSMFile().run_all(input)

    f_tagged = open(output, 'w+')
    f_tagged.write(GlobalVar.modified_text.getvalue())
    GlobalVar.modified_text.truncate(0)
    f_tagged.close()
