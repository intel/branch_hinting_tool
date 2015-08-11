#!/usr/bin/env python

import os
import sys

path = "."
os.system("rm -r "+ path + "all_folders")
os.system("mkdir " + path + "all_folders")
create_path= path + "/Zend/"

def generate(target):
	
	"""
		now I will change working directory to
		PHP's Zend folder
	"""
	os.chdir(target + "/Zend")
	dir_ls = os.listdir(".")
		
	""" Here we create a folder for each source or header file """
	command = "rm -r GCOVS/"
	print command
	os.system(command)		

	for i in range(len(dir_ls)):
		if dir_ls[i].endswith(".c") or dir_ls[i].endswith(".h"):
			#print dir_ls[i]
			
			command = "mkdir -p GCOVS/" + dir_ls[i] 
			print command
			os.system(command)
	

	""" Compile all the filename.c files and move all .gcov files into
	all_folders/folder_filename.c """
	
	for i in range(len(dir_ls)):
		if dir_ls[i].endswith(".c"):
			#print dir_ls[i]
			gcov_command = "gcov -bcu -o .libs/ " + dir_ls[i] + " &> /dev/null"
			print gcov_command
			os.system(gcov_command)
		
			command = "mv *.gcov " + "GCOVS/" + dir_ls[i] + "/"
			print command
			os.system(command)

	""" Move each header file to it's own folder """
	all_folders = os.listdir("GCOVS")
	os.chdir("GCOVS")
	#print all_folders

	
	for i in range(len(all_folders)):
		if all_folders[i].endswith(".c"):
			files_inside = os.listdir(all_folders[i])
			#print header_files_inside
			for j in range(len(files_inside)):
				if files_inside[j].endswith(".h.gcov"):
					mv_command = "mv " + all_folders[i] + "/" + files_inside[j] + " " + files_inside[j][:-5] +"/" + all_folders[i]+"_"+files_inside[j]
					os.system(mv_command)
					#print mv_command
