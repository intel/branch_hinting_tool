import os
import constants

def start(args):

    OLD_opt_flag = "-O2"
    NEW_opt_flag = "-O0"
    OLD_prof_flag = "-fprofile-generate"
    NEW_prof_flag = "--coverage"
    CONT = ""
    DEST = None
    PATH = ""

    if 'dest' in args and args['dest'] != None :
        DEST = args['dest']

    if 'path' in args and args['path'] != None :
        PATH = args['path']

    if DEST != None:
        print "LCOV destination folder: " + DEST
        command = "rm -r " + DEST + "/lcov_results"
        os.system(command)
        print command

        command = "mkdir -p " + DEST + "/lcov_results/html"
        os.system(command)
        print command

    for key in args:
        print key + ":" +args[key]

    print "Changind directory to " + PATH
    os.chdir(PATH)

    command = "sed \"s/" + OLD_opt_flag + "/" + NEW_opt_flag +"/g\"" " \"Makefile\" > Makefile.copy"
    os.system(command)
    print command

    os.system("cp Makefile.copy Makefile")

    command = "sed \"s/" + OLD_prof_flag + "/" + NEW_prof_flag +"/g\"" " \"Makefile\" > Makefile.copy"
    os.system(command)
    print command

    os.system("cp Makefile.copy Makefile")
    os.system("make clean")
    print constants.Constants.IR.toString()
    command = constants.Constants.IR.getRule("Makefile.RULE")  #+" &> /dev/null"
    os.system(command)
    print command

    os.system("pwd")
    command =  constants.Constants.IR.getRule("Config.COMMAND") # + " &> /dev/null"
    os.system(command)
    print command

    """
    #print "Destination: "+DEST + "\nPATH: "+PATH
    if DEST != None :
        command = "lcov --directory " + PATH + "/Zend/.libs/ " + "--rc lcov_branch_coverage=1 --capture --o " + DEST + "/lcov_results/results.lcov"
        os.system(command)
        print command

        command = "genhtml --branch-coverage -o " + DEST + "/lcov_results/html " + DEST + "/lcov_results/results.lcov"
        os.system(command)
        print command
    """
    os.system("rm Makefile.copy")


    """ redo initial makefile config
    command = "sed \"s/" + NEW_opt_flag + "/" + OLD_opt_flag +"/g\"" " \"Makefile\" > Makefile.copy"
    os.system(command)
    print command
    os.system("cp Makefile.copy Makefile")

    command = "sed \"s/" + NEW_prof_flag + "/" + OLD_prof_flag +"/g\"" " \"Makefile\" > Makefile.copy"
    os.system(command)
    print command
    os.system("cp Makefile.copy Makefile")
     """
