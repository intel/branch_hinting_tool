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

import argparse
import collect_statistics
import os
import instrument
import generate_csv
import parse
import ini
import constants
import blacklist


def main():
    parser = argparse.ArgumentParser(description='Stats collector')
    parser.add_argument(
        'filename', metavar='filename', type=str, nargs='+',
        help='filename or path to folder( pass -z if folder is PHP folder')
    parser.add_argument('-l', metavar='LOWER', type=int, nargs='?',
                        help='lower limmit acceptable limit for expected')
    parser.add_argument('-u', metavar='UPPER', type=int, nargs='?',
                        help='upper limmit acceptable limit for unexpected')
    parser.add_argument('-p', action='store_true', help='parse and build')
    parser.add_argument('-r', action='store_true', help='run the workload')
    parser.add_argument('-v', action='store_true', help='verbose')
    parser.add_argument('-a', action='store_true',
                        help='does parse, build and run(equivalent with -p -r)')
    parser.add_argument('-i', metavar='PATH_TO_INI_FILE',
                        type=str, nargs='?', help='ini file path')

    args = parser.parse_args()

    collect_statistics.FILENAME = args.filename[0]
    constants.PATH_TO_SOURCES = args.filename[0]
    lower_limit = args.l
    upper_limit = args.u
    ini_path = args.i
    constants.Constants.PATH_TO_SOURCES = args.filename[0]
    if args.a:
        args.p = True
        args.r = True

    # sets lower and upper limit for EXPECTED/UNEXPECTED percentage
    if upper_limit != None:
        constants.Constants.EXPECTED_LIMIT = upper_limit
        collect_statistics.EXPECTED_LIMIT = upper_limit
    if lower_limit != None:
        constants.Constants.UNEXPECTED_LIMIT = lower_limit
        collect_statistics.UNEXPECTED_LIMIT = lower_limit

    # e
    if ini_path != None:
        constants.Constants.DEFAULT_INI_FILE = ini_path

    constants.Constants.IR = ini.IniReader(
        constants.Constants.DEFAULT_INI_FILE)
    constants.Constants.IR.read()
    constants.Constants.BR = blacklist.BlacklistReader(
        constants.Constants.IR.get_rule("Config.BLACKLIST"))
    constants.Constants.BR.read()
    constants.Constants.IR.to_string()
    #   LIKELY and UNLIKELY contains the lists with all versions of macros
    # you use in code for _buildin_expected
    constants.Constants.LIKELY = constants.Constants.IR.get_rule(
        "Config.LIKELY").split(" ")
    constants.Constants.UNLIKELY = constants.Constants.IR.get_rule(
        "Config.UNLIKELY").split(" ")
    if '' in constants.Constants.LIKELY:
        constants.Constants.LIKELY.remove('')
    if '' in constants.Constants.UNLIKELY:
        constants.Constants.UNLIKELY.remove('')

    # edits and tags branches
    working_folder = constants.Constants.IR.get_rule(
        "Environment.WORKING_FOLDER")
    if working_folder.endswith("/") == False and os.path.isdir(working_folder):
        working_folder += "/"
    if not constants.Constants.PATH_TO_SOURCES.endswith("/") and os.path.isdir(
            constants.Constants.PATH_TO_SOURCES):
        constants.Constants.PATH_TO_SOURCES += "/"
    if os.path.exists(working_folder) and args.p:
        raise SystemError(working_folder + " exists."
                          + " Remove or specify another path in ini file.")

    sources = constants.Constants.PATH_TO_SOURCES
    constants.Constants.PATH_TO_SOURCES = working_folder

    if args.p == True:
        print "\nwith -p\n"
        #create working folder and copy content in it
        command = "mkdir " + working_folder
        print command
        os.system(command)

        if os.path.isdir(sources):
            sources += "*"

        command = "cp -r " + sources + " " + working_folder
        print command
        os.system(command)

        # prepare script
        if constants.Constants.IR.get_rule(
                "Environment.PREPARE_SCRIPT").endswith(".py"):
            command = "python " \
                + constants.Constants.IR.get_rule("Environment.PREPARE_SCRIPT")
        else:
            command = "./" + \
                constants.Constants.IR.get_rule("Environment.PREPARE_SCRIPT")

        print command
        if args.v == False:
            command += " > /dev/null"

        os.system(command)

        print "Parse sources for isolating atomic conditions one per line ..."
        parse.start(constants.Constants.PATH_TO_SOURCES)

    # build/ compile the filename or
    # files contained in the filename(when it's a folder)
    # using with intstrument.py
    instrument.instrument(constants.Constants.PATH_TO_SOURCES,
                          args.v, args.p, args.r)

    if args.r:
        # Generate csv file/s
        print "Aggregate CSV statistics ..."
        if os.path.isdir(constants.Constants.PATH_TO_SOURCES):
            generate_csv.apply_on_folder(os.path.join(
                constants.Constants.PATH_TO_SOURCES, "GCOVS"))

        else:
            generate_csv.generate(
                constants.Constants.PATH_TO_SOURCES + ".gcov")
        # handles the format of output
        collect_statistics.collect(os.path.join(
            constants.Constants.PATH_TO_SOURCES, "GCOVS/"))

if __name__ == "__main__":
    main()
