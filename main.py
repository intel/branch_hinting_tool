#!/usr/bin/env python

import argparse
import collect_statistics
import sys
import os
import instrument
import generate_csv
import parse
import ini
import constants
import blacklist


def main():
    wrongUnexp = False
    wrongExp = False
    right = False
    raw = False
    folder = False
    zend = False
    parser = argparse.ArgumentParser(description='Stats collector')
    parser.add_argument('filename', metavar='filename', type=str, nargs='+',
                        help='filename or path to folder( pass -z if folder is PHP folder')
    parser.add_argument('-l', metavar='LOWER', type=int, nargs='?', help='lower limmit acceptable limit for expected')
    parser.add_argument('-u', metavar='UPPER', type=int, nargs='?', help='upper limmit acceptable limit for unexpected')
    parser.add_argument('-F', action='store_true', help='apply on folder')
    parser.add_argument('-p', action='store_true', help='use the parser to parse the files')
    parser.add_argument('-v', action='store_true', help='verbose')
    parser.add_argument('-a', action='store_true', help='returns output in csv format')
    parser.add_argument('-d', metavar='PATH', type=str, nargs='?', help='PATH where we put the LCOV RESULTS')
    parser.add_argument('-i', metavar='PATH_TO_INI_FILE', type=str, nargs='?', help='ini file path')

    args = parser.parse_args()

    collect_statistics.FILENAME = args.filename[0]
    constants.PATH_TO_SOURCES = args.filename[0]
    lowerLimit = args.l
    upperLimit = args.u
    folder = args.F
    all = args.a
    lcovPath = args.d
    iniPath = args.i
    constants.Constants.PATH_TO_SOURCES = args.filename[0]

    #sets lower and upper limit for EXPECTED/UNEXPECTED percentage
    if lowerLimit != None:
        collect_statistics.EXPECTED_LIMIT = lowerLimit

    if upperLimit != None:
        collect_statistics.UNEXPECTED_LIMIT = upperLimit

    #e
    if iniPath != None:
        constants.Constants.DEFAULT_INI_FILE = iniPath

    constants.Constants.IR = ini.IniReader(
                            constants.Constants.DEFAULT_INI_FILE)
    constants.Constants.IR.read()
    constants.Constants.BR = blacklist.BlacklistReader(
                            constants.Constants.IR.get_rule("Config.BLACKLIST"))
    constants.Constants.BR.read()
    constants.Constants.IR.to_string()

    """ edits and tags branches """
    working_folder = constants.Constants.IR.get_rule("Environment.WORKING_FOLDER")
    if working_folder.endswith("/") == False and os.path.isdir(working_folder):
        working_folder += "/"
    if constants.Constants.PATH_TO_SOURCES.endswith("/") == False and os.path.isdir(
            constants.Constants.PATH_TO_SOURCES):
        constants.Constants.PATH_TO_SOURCES += "/"
    if os.path.exists(working_folder):
        raise SystemError(working_folder + " exists."
                          +" Remove or specify another path in ini file.")

    """
    create working folder and copy content in it
    """
    command = "mkdir " + working_folder
    print command
    os.system(command)

    sources = constants.Constants.PATH_TO_SOURCES

    if os.path.isdir(constants.Constants.PATH_TO_SOURCES):
        sources += "*"

    command = "cp -r " + sources +" "+ working_folder
    print command
    os.system(command)

    """
        now we have copied sources into working folder.
        Working folder will be our current working directory
    """
    constants.Constants.PATH_TO_SOURCES = working_folder

    """
        prepare script
    """
    if constants.Constants.IR.get_rule("Environment.PREPARE_SCRIPT").endswith(".py"):
        command = "python " \
                  + constants.Constants.IR.get_rule("Environment.PREPARE_SCRIPT")
    else:
        command = "./" + constants.Constants.IR.get_rule("Environment.PREPARE_SCRIPT")

    if args.v == False:
        command += " &> /dev/null"

    os.system(command)


    if args.p == True:
        parse.start(constants.Constants.PATH_TO_SOURCES)



    """ build/ compile the filename or
        files contained in the filename(when it's a folder)
        using with intstrument.py
    """

    instrument.instrument(constants.Constants.PATH_TO_SOURCES, lcovPath, args.v)

    """
        Generate csv file/s
    """
    # print filename
    # print os.system("ls ")
    if os.path.isdir(constants.Constants.PATH_TO_SOURCES):
        generate_csv.apply_on_folder(os.path.join(constants.Constants.PATH_TO_SOURCES, "GCOVS"))

    else:
        generate_csv.generate(constants.Constants.PATH_TO_SOURCES + ".gcov")
    """
        handles the format of output
    """
    collect_statistics.collect(os.path.join(constants.Constants.PATH_TO_SOURCES, "GCOVS/"))

if __name__ == "__main__":
    main()
