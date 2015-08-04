#!/usr/bin/env python

import os
import sys
sys.path.insert(0, 'branch_tagger')
import apply_fsm_file
import apply_on_folder

original_path = "Zend"
save_path = "Zend_modified" 
FILENAME = ""

def main(argv=sys.argv):
	global original_path, save_path
	if len(sys.argv) != 3:
		print "Change script vars or call this with parameters"
	else:
		original_path = sys.argv[1]
		save_path = sys.argv[2]
#	start()

def start(filename, zend):
	global FILENAME, original_path, save_path

	if zend == True:
		original_path = filename + "Zend"
		save_path = filename + "/Zend_modified"
	if os.path.isdir(filename) == True:
		#os.system(" rm -r " + save_path)
		#os.system("rm -r " + original_path + "_copy")
		#os.system("cp -r " + original_path + " " + original_path + "_copy")
		#command = "mkdir " + save_path
		#os.system(command)
		#dir_ls = os.listdir(original_path)
		#ApplyFSMFolder(original_path)
		#for i in range(len(dir_ls)):
		#	if dir_ls[i].endswith(".c") or dir_ls[i].endswith(".h"):		
		#		print "Processing " + dir_ls[i]		
		#		command = "java -jar parser.jar " + original_path + "/" + dir_ls[i] + " " + save_path + "/" +dir_ls[i]		
		#		os.system(command)
		os.chdir("branch_tagger")
		command = " python apply_on_folder.py " + original_path + "/"
		print command
		os.system(command)
		os.chdir("..")
		print "Done processing for all files"
		#os.system("cp " + save_path +"/*.c " + original_path)
		#os.system("cp " + save_path +"/*.h " + original_path)
		#os.system("rm -r " + original_path)
		#os.system("cp -r " + original_path + "_copy " + original_path)
		#os.system("rm -r " + original_path + "_copy")
		#os.system("rm -r " + save_path)
	else :
		print "File processing"
		os.chdir("branch_tagger")
		command = " python apply_on_folder.py " + filename
		os.system(command) 
		os.chdir("..")

#if __name__ == "__main__" :
#start(sys.argv[1], sys.argv[2])
