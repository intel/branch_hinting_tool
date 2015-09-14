import os
import constants

"""
    1. replaces -O2 with -O0 and -fprofile-generate with --coverage.
    2. builds the project.
    3. run workload with binary obtained at step 1
    4. redo initial configuration for Makefile
"""


def start(args, verbose, build, run):
    if build:
        OLD_opt_flag = "-O2"
        NEW_opt_flag = "-O0"
        OLD_prof_flag = "-fprofile-generate"
        NEW_prof_flag = "--coverage"
        CONT = ""
        DEST = None
        PATH = ""

        if 'dest' in args and args['dest'] != None:
            DEST = args['dest']

        if 'path' in args and args['path'] != None:
            PATH = args['path']

        if DEST != None:
            print "LCOV destination folder: " + DEST
            command = "rm -r " + os.path.join(DEST, "/lcov_results")
            os.system(command)
            print command

            command = "mkdir -p " + os.path.join(DEST, "lcov_results/html")
            os.system(command)
            print command

        for key in args:
            print key + ":" + args[key]

        if verbose:
            print "Changind directory to " + PATH
        os.chdir(PATH)

        command = "sed \"s/" + OLD_opt_flag + "/" + NEW_opt_flag \
                  + "/g\"" " \"Makefile\" > Makefile.copy"
        os.system(command)
        if verbose:
            print command

        os.system("cp Makefile.copy Makefile")

        command = "sed \"s/" + OLD_prof_flag + "/" + NEW_prof_flag \
                  + "/g\"" " \"Makefile\" > Makefile.copy"
        os.system(command)
        if verbose:
            print command

        os.system("cp Makefile.copy Makefile")
        os.system("make clean")
        if verbose:
            print constants.Constants.IR.to_string()

        command = constants.Constants.IR.get_rule("Makefile.RULE")
        if verbose == False:
            command += " &> /dev/null"
        os.system(command)

        if verbose:
            print command

    if run:
        os.system("pwd")
        command = constants.Constants.IR.get_rule("Config.COMMAND")

        if verbose ==  False:
            command += " &> /dev/null"
        os.system(command)

        if verbose:
            print command

    #os.system("rm Makefile.copy")