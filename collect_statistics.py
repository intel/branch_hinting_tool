#!/usr/bin/env python

"""
DOES THE SUM OF 2 CSV FILES(ON 3RD AND 4TH
COLUMN BASED ON  EQUALITY ON 1ST COLUMN)
"""

import argparse
import sys
import os
import collections
import constants
FILENAME = ""
FILENAME_OUT = ""
file1 = None
hmap = {}
EXPECTED_LIMIT = 40 # limit for branch taken 
UNEXPECTED_LIMIT = 60 # limit for branch not taken


"""
def applyOnFolder(folder, zend):
	global FILENAME, FILENAME_OUT
	FILENAME = folder + "/stats.csv"
	FILENAME_OUT =  folder + "/stats.output"
	cstat = Collector()
	if zend == True:
		old_path = os.getcwd()
		os.chdir(folder + "/Zend/GCOVS")
		all_folders = os.listdir(".")
		for i in range(len(all_folders)):
			path = folder + "/Zend/GCOVS/" + all_folders[i] + "/" +all_folders[i] + "_sum_.csv"
			print "Added " + path
			cstat.addFile(path)
		os.chdir(old_path)
		cstat.writeCSV()
		cstat.writeOutput()

	elif os.path.isdir(folder):
		dir_ls = os.listdir(folder)
		old_path = os.getcwd()
		os.chdir(folder)
		for i in range(len(dir_ls)):
			if dir_ls[i].endswith(".csv") :		
				cstat.addFile(dir_ls[i])
		os.chdir(old_path)
	else:
		cstat.addFile(folder + ".csv")
	
	return cstat
"""
class Condition():

	def __init__(self, filename, line, tpe, br0, br1, pr):
		self.filename = filename
		self.line = line
		self.type = tpe
		self.branch0 = br0
		self.branch1 = br1
		self.proc = pr
		self.state = constants.MISSING

	def toString(self):
		s = self.filename + " "
		s += "line " + str(self.line) + " :\n"
		if self.type == 0 :
			s += "\tType : EXPECTED\n"
		else:
			s += "\tType : UNEXPECTED\n"
		s += "\tTimes Taken : \n\t\tBranch 0: " + str(self.branch0) + "\n\t\tBranch 1: " + str(self.branch1) + "\n"
		s += "\tPercent times taken: " + str(self.proc) + "%\n"
		return s

class Collector():

	def __init__(self) :
		self.map = {}
		self.file = None
		self.wrongExpected = []
		self.wrongUnexpected = []
		self.rightPredicted = []

	def printWrongExpected(self):
		print "-=====- WRONG EXPECTED -=====-\n"
		for c in self.wrongExpected:
			print c.toString()

	def printWrongUnexpected(self):
		print "-=====- WRONG UNEXPECTED -=====-\n"
		for c in self.wrongUnexpected:
			print c.toString()

	def printRightPredicted(self):
		print "-=====- RIGHT PREDICTIONS -=====-\n"
		for c in self.rightPredicted:
			print c.toString()

	def printAll(self):
		self.printWrongExpected()
		self.printWrongUnexpected()
		self.printRightPredicted()
	
	def addFile(self, path, filename):
		try:
			self.file = open(filename , 'r')
		except:
			print "error while opening the files"
			raise
		fname = filename[:-4]
		content = self.file.read().splitlines()
		for i in range(len(content)) :
			if i == 0 :
				continue

			lista = content[i].split(", ")
			line = int(lista[0])
			proc = int(float(lista[1]))
			b0 = int(lista[2])
			b1 = int(lista[3])
			exp = lista[4]
			num_br = int(lista[5])
			key = fname + ", " + str(line)
			if key in self.map:
				b0 += self.map[key][5] 
				b1 += self.map[key][6]
				proc =  round( b0 * 100/ (b0 + b1), 0)
			#if "GCOVS" in path:
			#	print path
			path = path.replace("/GCOVS/", "/")
			if num_br > 2 :
				mod_line = [constants.OVERFLOW , exp, constants.NONE, (b0 + b1), proc, b0, b1,  lista[5], lista[6], lista[7], path]
			elif exp == constants.EXPECTED and proc < EXPECTED_LIMIT:
				self.wrongExpected.append(Condition(filename, line, exp, b0, b1, proc))
				mod_line = [constants.WRONG, exp, constants.UNEXPECTED , (b0 + b1) , proc, b0, b1, lista[5], lista[6], lista[7], path]
			elif exp == constants.UNEXPECTED and proc > UNEXPECTED_LIMIT:
				self.wrongUnexpected.append(Condition(filename, line, exp, b0, b1, proc))
				mod_line = [constants.WRONG, exp, constants.EXPECTED , (b0 + b1) , proc, b0, b1, lista[5], lista[6], lista[7], path]
			elif (exp == constants.EXPECTED and proc > EXPECTED_LIMIT) or\
				(exp == constants.UNEXPECTED and proc < UNEXPECTED_LIMIT):
				self.rightPredicted.append(Condition(filename, line, exp, b0, b1, proc))
				mod_line = [constants.CORRECT, exp, exp, (b0 + b1), proc, b0, b1, lista[5], lista[6], lista[7], path]
			else :
				if proc < (UNEXPECTED_LIMIT + EXPECTED_LIMIT)/2 :
					mod_line = [constants.MISSING, exp, constants.UNEXPECTED, (b0 + b1), proc, b0, b1, lista[5], lista[6], lista[7], path]
				else :
					mod_line = [constants.MISSING, exp, constants.EXPECTED, (b0 + b1), proc, b0, b1, lista[5], lista[6], lista[7], path]
			#print len(mod_line)
			self.map[key] = mod_line

	def writeOutput(self):
		try:
  			ofile = open(FILENAME_OUT, 'w')
  		except:
  			print FILENAME_OUT + " - Write to file: error opening file for write\n"
  			raise

		for key in self.map :
			s = str(key[0]) + " / Line " + str(key[0]) + ": " + str(self.map[key][0]) + "\n"
			if self.map[key][0] == constants.WRONG or self.map[key][0] == constants.MISSING :
				s += "Expected Hint: " + self.map[key][2] + "(Taken" + str(self.map[key][4]) + "%) instead of " + self.map[key][1] +"\n"
			elif self.map[key][0] == constants.CORRECT :
				s += "Current Hint: " + self.map[key][1] + "\n"
			s +=  "Total: " + str(self.map[key][3]) + " / Taken: " + str(self.map[key][5]) + "(" + str(self.map[key][4]) + "%) / Not Taken: " +  str(self.map[key][6]) + " (" + str(100-self.map[key][4]) + "%)\n\n"
			ofile.write(s)

	def writeCSV(self,FILENAME):
		print "HEIL: " + FILENAME
		try:
  			wfile = open(FILENAME, 'w')
  		except:
  			print FILENAME + " - Write to file: error opening file for write\n"
  			raise
  		s = "PATH, FILENAME, LINE, STATE, CUrRENT HINT, EXPECTED HINT, TOTAL #, TAKEN % , TAKEN, NOT TAKEN, NUM_BRANCHES, BRANCH TYPE, LINE OF CODE\n"
		wfile.write(s)

		for key in self.map:
			s = self.map[key][10] + ", " + str(key) + ", " + self.map[key][0] + ", " + str(self.map[key][1]) + ", " + str(self.map[key][2]) + ", " + str(self.map[key][3]) + ", " + str(self.map[key][4]) + ", " + str(self.map[key][5]) + ", " + str(self.map[key][6]) + ", " + str(self.map[key][7])  + ", " + str(self.map[key][8]) + ", " + str(self.map[key][9]) + "\n"
			wfile.write(s)

		def getMap(self):
			return self.map



cstat = Collector()

def applyOnFolder(target):
	global cstat
	old_path = os.getcwd()
	os.chdir(target)
	#print os.getcwd()
	dir_ls = os.listdir(".")
	for item in dir_ls:
		if os.path.isdir(item):
			applyOnFolder(target + "/" + item)
		elif item.endswith(".c.csv") or item.endswith(".h.csv"):
			cstat.addFile(old_path, item)

	os.chdir(old_path)

def collect(target):
	applyOnFolder(target)
	cstat.writeCSV(target + "/statistics.csv")

#applyOnFolder(sys.argv[1], True)
