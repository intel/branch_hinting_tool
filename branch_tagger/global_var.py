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

# Keeps all the global variables
from cStringIO import StringIO


class GlobalVar:
    def __init__(self):
        pass

    modified_text = StringIO()

    count_paren = 1

    if_condition = False
    while_condition = False
    for_condition = False

    in_preprocessor = False
    in_string = False

    in_comment = False

    comment = False

    line_comment = False
    condition = StringIO()
