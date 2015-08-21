#!/usr/bin/env python
import sys

import constants

sys.path.insert(0, 'branch_tagger')
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

def start(target):

	apply_on_folder.apply(target, constants.Constants.BLACKLIST)
