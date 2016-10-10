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

import os
import sys
import generate_gcov
import constants
import autogen
# import oldVersion_generate_gcov

def instrument(target, flags, verbose, build, run):
    if os.path.isdir(target):
        autogen.start({'path': target}, verbose,build, run)
        # aici trebuie sa adaug generate_gcov
        print "Collect GCOV statistics ..."
        generate_gcov.generate(target, verbose, run)

    else:
        command = "gcc -fprofile-arcs -ftest-coverage " \
                  + target + " -o " + target + ".o"
        print command
        os.system(command)
        command = "./" + target + ".o"
        print command
        os.system(command)
        command = "gcov -bcu " + target
        print command
        os.system(command)
