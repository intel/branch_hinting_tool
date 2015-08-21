#!/usr/bin/env python

import os
import sys
import constants

path = "."
os.system("rm -r "+ path + "all_folders")
os.system("mkdir " + path + "all_folders")
create_path= path + "/Zend/"

def generate(target):
	
	old_path = os.getcwd()
	os.chdir(target)
	dir_ls = os.listdir(".")
		
	""" Here we create a folder for each source or header file """
	command = "rm -r GCOVS/"
	#print command
	os.system(command)		
	
	recursive(target, target + "/GCOVS", target)
	
def recursive(target, dest, build_path):
	"""
		now I will change working directory to
		PHP's Zend folder
	"""
	old_path = os.getcwd()
	os.chdir(target)
	dir_ls = os.listdir(".")
	#print os.getcwd()
	for item in dir_ls:
		if item.endswith(".c") or item.endswith(".cpp"):
			command = "mkdir -p " + dest + "/" + item
		#	print command
			os.system(command)
		if item.endswith(".c") or item.endswith(".cpp"):
			#save the current path
			current_path = os.getcwd()

			#go to build path
			os.chdir(build_path)
			gcov_command = "gcov -bcu -o " + current_path + "/" + constants.Constants.IR.getRule("Config.LIBS") + " " + current_path + "/" + item #+ " &> /dev/null"
			print gcov_command

			os.system(gcov_command)
			move_command = " mv *.gcov " + dest + "/" + item
			print move_command
			os.system(move_command)

			#go back to current path
			os.chdir(current_path)

		if os.path.isdir(item) and "GCOVS" not in item:
			recursive(item, dest + "/" + item, build_path)
	os.chdir(old_path)

#generate(sys.argv[1])







