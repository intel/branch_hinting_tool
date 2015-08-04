#!/usr/bin/env python

import os
import sys
import generate_gcov
import oldVersion_generate_gcov
FLAGS = ""
target = ""
zend_make_script = "autogenerate.py"

""" This method calls the autogenerate script
	where the .gcda/b and .gcno files are
	created for profiling.
	In order to use gcov, you must compile all
	the sources with --coverage flag or
	-fprofile-arcs and -ftest-coverage
"""
def instrument(target, zend, flags):
	global FLAGS
	if flags != "" and flags != None :
		FLAGS = " -d " + flags
	if zend == True:
		command = "./" + zend_make_script + " -p " + target + FLAGS
		print command
		os.system(command)
		# aici trebuie sa adaug generate_gcov
		generate_gcov.generate(target)

	elif os.path.isdir(target) :
		dir_ls = os.listdir(target)
		old_path = os.getcwd()
		os.chdir(target)
		for i in range(len(dir_ls)):
			if dir_ls[i].endswith(".c") :		
				print "Processing "+ dir_ls[i]		
				command = "gcc -fprofile-arcs -ftest-coverage " + dir_ls[i] + " -o " + dir_ls[i] + ".o"
				os.system(command)
				os.system("./" + dir_ls[i] + ".o")
				command = "gcov -bcu " + dir_ls[i]
				os.system(command)
		os.chdir(old_path)

		
	else :
		command = "gcc -fprofile-arcs -ftest-coverage " + target + " -o " + target + ".o"
		os.system(command)
		os.system("./" + target + ".o")
		command = "gcov -bcu " + target
		os.system(command)

