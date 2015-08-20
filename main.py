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
def main():
	wrongUnexp = False
	wrongExp = False 
	right = False
	raw = False
	folder =  False
	zend = False
	parser = argparse.ArgumentParser(description='Stats collector')
	parser.add_argument('filename', metavar='filename', type=str, nargs='+', help='filename or path to folder( pass -z if folder is PHP folder')
	parser.add_argument('-l', metavar='LOWER', type=int, nargs='?', help='lower limmit acceptable limit for expected')
	parser.add_argument('-u', metavar='UPPER', type=int, nargs='?', help='upper limmit acceptable limit for unexpected')
	parser.add_argument('-F', action='store_true', help='apply on folder')
	parser.add_argument('-pu', action='store_true', help='prints only those conditions tagged WRONG as UNEXPECTED')
	parser.add_argument('-pe', action='store_true' , help='prints only those conditions tagged WRONG as EXPECTED')
	parser.add_argument('-pc', action='store_true', help='prints only those conditions RIGHT')
	parser.add_argument('-a',  action='store_true', help='returns output in csv format')
	parser.add_argument('-d', metavar='PATH', type=str, nargs='?', help='PATH where we put the LCOV RESULTS')
	parser.add_argument('-i', metavar='PATH_TO_INI_FILE', type=str, nargs='?', help='ini file path')

	args = parser.parse_args()

	collect_statistics.FILENAME = args.filename[0]
	filename = args.filename[0]
	lowerLimit = args.l
	upperLimit = args.u
	folder =  args.F
	wrongExp = args.pe
	wrongUnexp = args.pu
	right = args.pc
	all = args.a
	lcovPath = args.d
	iniPath = args.i

	if lowerLimit != None:
		collect_statistics.EXPECTED_LIMIT = lowerLimit

	if upperLimit != None:
		collect_statistics.UNEXPECTED_LIMIT = upperLimit

	if iniPath != None:
		constants.DEFAULT_INI_FILE = iniPath


	""" edits and tags branches """
	parse.start(filename)



	""" build/ compile the filename or
		files contained in the filename(when it's a folder) 
		using with intstrument.py
	"""

	instrument.instrument(filename, lcovPath)

	"""
		Generate csv file/s
	"""
	#print filename
	#print os.system("ls ")
	if os.path.isdir(filename) :
		generate_csv.applyOnFolder(filename + "GCOVS")

	else :
		generate_csv.generate(filename + ".gcov")

	"""
		handles the format of output
	"""
	collect_statistics.collect(filename + "/GCOVS/")
	"""
	if all == True and cstat != None:
		cstat.printAll()
	
	if wrongExp == True and cstat != None:
		cstat.printWrongExpected()

	if wrongUnexp == True and cstat != None:
		cstat.printWrongUnexpected()

	if right == True and cstat != None:
		cstat.printRightPredicted()
	"""
	#EXPECTED_LIMIT = int(sys.argv[2])
	#UNEXPECTED_LIMIT = int(sys.argv[3])

if __name__ == "__main__":
	main()
