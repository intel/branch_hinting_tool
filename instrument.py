#!/usr/bin/env python

import os
import sys
import generate_gcov
#import oldVersion_generate_gcov
FLAGS = ""
target = ""
zend_make_script = "autogenerate.py"
def instrument(target, flags):
	global FLAGS
	if flags != "" and flags != None :
		FLAGS = " -d " + flags
	if os.path.isdir(target) :
		command = "./" + zend_make_script + " -p " + target + FLAGS
		print command
		os.system(command)
		# aici trebuie sa adaug generate_gcov
		generate_gcov.generate(target)
#		oldVersion_generate_gcov.generate(target)

	else :
		command = "gcc -fprofile-arcs -ftest-coverage " + target + " -o " + target + ".o"
		os.system(command)
		os.system("./" + target + ".o")
		command = "gcov -bcu " + target
		os.system(command)

