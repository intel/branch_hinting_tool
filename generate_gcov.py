#!/usr/bin/env python

import os
import sys

path = "."
os.system("rm -r "+ path + "all_folders")
os.system("mkdir " + path + "all_folders")
create_path= path + "/Zend/"

"""	This method creates the GCOVS folder
	and calls the recursive method with
	target folder(initial folder where all
	the instrumented sources are) and
	destination folder (where .gcovs and
	.csv will be placed)
"""
def generate(target):
	
	old_path = os.getcwd()
	os.chdir(target)
	dir_ls = os.listdir(".")
		
	""" Here we create a folder for each source or header file """
	command = "rm -r GCOVS/"
	print command
	os.system(command)		
	
	recursive(target, target + "/GCOVS")

"""
	This method executes cd on each directory found
	and gcov on each .c / .cpp file
"""
def recursive(target, dest):

	old_path = os.getcwd()
	os.chdir(target)
	dir_ls = os.listdir(".")
	print os.getcwd()	
	for item in dir_ls:
		if item.endswith(".c") or item.endswith(".cpp"):
			command = "mkdir -p " + dest + "/" + item
			print command
			os.system(command)
		if item.endswith(".c") or item.endswith(".cpp"):
			gcov_command = "gcov -bcu -o .libs/ " + item + " &> /dev/null"
			print gcov_command
			os.system(gcov_command)	

			move_command = " mv *.gcov " + dest + "/" + item
			print move_command
			os.system(move_command)

		if os.path.isdir(item) and "GCOVS" not in item:
			recursive(item, dest + "/" + item)
	os.chdir(old_path)

#generate(sys.argv[1])







