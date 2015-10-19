############################################################################
# Branch Hinting Tool
#
# Copyright (c) 2015, Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
###########################################################################

#!/usr/bin/env python
import os
import sys
import calculs
import constants
import re
filename = ""
interestingConds = []
csvOutput = ""
rawOutput = ""


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_line_no(line):
    regex = re.compile(r"[*][0-9]+[:][ ]")
    m = regex.search(line)
    if m is not None:
        index_star = m.start()
        index_points = m.end()
        return line[index_star + 1:index_points - 2]
    return "0"
"""
def get_line_no(line):
	list = line.split("
	no = "0"
	if len(list) <= 1:
		no = "0"
	else:
		number = list[len(list)-1].strip().rstrip()
		if isInt(number):
			no = number
	return no
"""

def apply_on_folder(target):

	old_path = os.getcwd()
	os.chdir(target)
	#print os.getcwd()
	dir_ls = os.listdir(".")
	for item in dir_ls:
		if os.path.isdir(item):
			apply_on_folder(target + "/" + item)
		elif item.endswith(".gcov"):
			generate(item)
	os.chdir(old_path)


def generate(fname):

	global filename, rawOutput, csvOutput
	if len(fname)  <= 0 or fname == None:
		print "You must give filename parameter"
		exit()

	filename = fname
	csvOutput = fname[:-5] + ".csv"
	rawOutput = fname[:-5] + ".output"

	parser = Parser(filename)
	parser.start()

	"""We have all the conditions in text in parser.conds list"""
	conds = parser.conditii

	#printConds(parser.conditii)

	filtru = Filter(conds)
	filtru.remove_non_branch()
	filtru.remove_call()
	filtru.remove_never_executed()
	filtru.compute()

	cc = Classifier(filtru.interestingConds)
	cc.classify_expected()

	log = Logger(filtru.interestingConds,
                 filtru.onlyNeverExecuted, csvOutput, rawOutput)
	log.create_log_files()
	log.start()


	nrI = len(filtru.interestingConds)
	nrN	= len(filtru.onlyNeverExecuted)
	total = nrN + nrI
	if total != 0 :
		pI = round(nrI * 100.0 / total, 2)
		pN = round(nrN * 100.0 / total, 2)
	else:
		pI = pN = 0
	"""
	print "\n\nStatistics:\n\tExecuted: " + str(pI) \
          + "% (" + str(nrI) + " conditions)"
	print "\tNever Executed: " + str(pN) + "% (" \
          + str(nrN) + " conditions)"
	"""


class Branch:

	"""
		branch object:
			name (eg. branch 1, unconditional 2 etc.)
			number - branch number parsed from name

	"""
	def __init__(self, name ,number, prob):
		self.name = name
		self.number = number
		self.probability = prob
		self.timesExecuted = 0

	def set_name(self, nume):
		self.name = nume

	def get_name(self):
		return self.name

	def get_probability(self):
		return self.probability

	def get_times_executed(self):
		return self.timesExecuted

	def extract_times_executed(self):
		lista = self.name.split("taken")
		self.set_name(lista[0].strip())
		timesExec = lista[1].strip().split(" ")
		self.timesExecuted = int(timesExec[0])


		""" here we extract the number of each branch """
		alls = lista[0].split(" ")
		self.number = alls[len(alls)-2]
		#print int(timesExec[0])

	def compute_probability(self, nr):
		#print str(self.timesExecuted) + " -- " + str(nr)
		if "unconditional" not in self.name:
			self.probability = self.timesExecuted * 100.0 / nr
		else:
			self.probability = 0.0

class Condition:

	def __init__(self, test, line):
		self.test = test
		self.line = line
		self.branches = []
		self.sumBranches = 0
		self.type = constants.Constants.UNKNOWN
		self.multiCond = 0
		self.num_branches = 0
		self.expected = 2 # 0 - EXPECTED ; 1 - UNEXPECTED ; 2 - UNKNOWN

	def copy_condition(self, cond):
		self.test = cond.test
		self.line =	cond.line
		self.branches = cond.branches

	def set_test(self, test):
		self.test = test

	def set_multicond(self):
		self.multiCond = 1

	def reset_multicond(self):
		self.multiCond = 0

	def set_line(self,lineno):
		self.line = lineno

	def get_branches(self):
		return self.branches

	def add_branch(self,name, no, prob):
		self.branches.append(Branch(name,no,prob))

	def get_test(self):
		return self.test

	def compute_sum_branches(self):
		for br in self.branches:
			if "unconditional" not in br.get_name():
				self.num_branches +=1
				self.sumBranches += br.get_times_executed()

	def establish_type(self):
		if "if branch" in self.test:
			self.type = constants.Constants.IF
		elif "while branch" in self.test:
			self.type = constants.Constants.WHILE
		elif "for branch" in self.test:
			self.type = constants.Constants.FOR
		elif "?" in self.test: #conditional expression - might have some issues on C++ code
			self.type = constants.Constants.IF
		elif "weird condition" in self.test:
			self.type = constants.Constants.WEIRD

	def remove_branch(self, branch):
		self.branches.remove(branch)

	def get_branches_times_executed(self):
		lista = []
		for br in self.branches:
			if "unconditional" not in br.get_name():
				lista.append(br.get_times_executed())
		return lista

	def to_string(self):

		filen = filename.split("/")
		source_file = filen[len(filen) - 1][:-5]
		s = "\n" + source_file +"(line " + str(self.line) +\
            "):\n\tCondition: " + self.test +\
		    "\n\tType: " + self.type +\
		    "\n\t#Branches: " + str(self.num_branches) +\
		    "\n\tMulticond: " + str(self.multiCond) +\
		    "\n\tExpected: " + str(self.expected) +\
		    "\n\tBranches:"
		for br in self.branches :
			s += "\n\t\t" + str(br.number) + ": "+ br.name + " - " \
                 + str(round(br.probability,2)) + "% (" \
                 + str(br.get_times_executed()) +" times executed)"

		return s

	def print_condition(self):
		filen = filename.split("/")
		source_file = filen[len(filen) - 1][:-5]
		print "\n" + source_file +"(line " \
              + str(self.line) + "):\n\tCondition: " + self.test
		print "\tType: " + self.type
		print "\t#Branches: " + str(self.num_branches)
		print "\tMulticond: " + str(self.multiCond)
		print "\tBranches:"
		for br in self.branches :
			#print(" %i : %s - %.2f (%i times executed)")
			print "\t\t" + str(br.number) + ": "+ br.name + " - " \
                  + str(round(br.probability,2)) + "% (" \
                  + str(br.get_times_executed()) +" times executed)"

	def get_sum_branches(self):
		return self.sumBranches

	def reset(self):
		self.test = ""
		self.line = 0
		self.branches = []

class Parser:
	def __init__(self, path):
		self.path = filename
		self.conditii = []
		self.sharedcond = Condition("",0)
		#print "A parser for file " + self.path + " was created!"

	def start(self):
		#print "Started to parse gcov file..."

		with open(self.path) as f:
			content = f.read().splitlines()

		for i in range(len(content)-1):

			if (content[i].startswith("unconditional")
                or content[i].startswith("branch")
                or content[i].startswith("call") ) and\
			  (content[i-1].startswith("unconditional") == False
               and content[i-1].startswith("branch") == False
               and content[i-1].startswith("call") == False ) :
				#print "Test line "+str(i)+":\n"
				"""Split the line to find out the line number where the branch/call occurs"""
				lista = content[i-1].split(":")
				#print lista
				lineno = lista[1].strip().rstrip()
				test = lista[2].strip().rstrip()
				if len(lista) > 3:
					test += (":" + lista[3])
				#print test
				"""
				test = ""
				for i in range(len(lista)):
					if i > 1:
						test += lista[i] + ":"
				test = test.strip(":")
				"""
				self.sharedcond.set_test(test)
				self.sharedcond.set_line(lineno)

				#print content[i]
				self.sharedcond.add_branch(content[i],0,0)

				if content[i+1].startswith("unconditional") == False \
                    and content[i+1].startswith("branch") == False \
                    and content[i+1].startswith("call") == False :
					cond = Condition("",0)
					cond.copy_condition(self.sharedcond)
					self.conditii.append(cond)
					self.sharedcond.reset()
					#print "End test\n\n"

			elif	(content[i].startswith("unconditional")
                     or content[i].startswith("branch")
                     or content[i].startswith("call") ) and\
			  		(content[i+1].startswith("unconditional")
                     or content[i+1].startswith("branch")
                     or content[i+1].startswith("call") ) :
				self.sharedcond.add_branch(content[i],0,0)
				#print content[i]

			elif	(content[i].startswith("unconditional")
                     or content[i].startswith("branch")
                     or content[i].startswith("call ") ) and\
			  		(content[i+1].startswith("unconditional") == False
                     and content[i+1].startswith("branch") == False
                     and content[i+1].startswith("call ") == False ) :
				#print content[i]
				self.sharedcond.add_branch(content[i],0,0)

				cond = Condition("",0)
				cond.copy_condition(self.sharedcond)
				self.conditii.append(cond)
				self.sharedcond.reset()
				#print "End test\n\n"
		try:
			f.close()
		except:
			print "Unexpected file.close() error: ",sys.exec_info()[0]
			raise


class Filter:
	"""
			This class will filter the conditions eliminating
		all of those where information isn't needed for us or
		incomplete
	"""
	def __init__(self, conds):
		self.conditions = conds #the list with unfiltered conditions
		self.branchConds = []	#contains only conditions with at least 1 branch

		self.interestingConds = [] #useful conditions
		self.onlyNeverExecuted = [] #conditions with only never executed branches
		#print "Started to filter the conditions results..."

		# here we set conditions types (IF/WHERE/FOR)
		self.establish_conditions_type()


	"""
			add to branchConds the subset of conditions that contains
		at least one branch
	"""
	def remove_non_branch(self):
		for cond in self.conditions:
			ok = 0
			branches = []
			for br in cond.branches:
				if "branch" in br.get_name():
					ok = 1
			if ok == 1 :
				#print "got here"
				self.branchConds.append(cond)

	"""
		remove the each "call" considered condition branch
	"""
	def remove_call(self):
		for cond in self.branchConds:
			partialbr = []
			for br in cond.get_branches():
				text = br.get_name()
				if text.startswith("call") == False \
                   and text.startswith("unconditional") == False :
					partialbr.append(br)
			cond.branches = partialbr

	"""
			separates the conditions that were never executed from
		those with times executed != 0
	"""
	def remove_never_executed(self):
		for cond in self.branchConds:
			partialbr = []
			for br in cond.get_branches():
				text = br.get_name()
				if "never executed" not in text:
					partialbr.append(br)
			if len(partialbr) == 0:
				self.onlyNeverExecuted.append(cond)
			else:
				cond.branches = partialbr
				self.interestingConds.append(cond)

	"""
			extracts how many times each branch was executed
		and his execution probability for each condition
	"""
	def compute(self):
		""" makes the sum of all condition branches """
		for cond in self.interestingConds:
 			for br in cond.get_branches():
				br.extract_times_executed()

			cond.compute_sum_branches()
			total = cond.get_sum_branches()
			""" computes the probability for each branch of actual condition """
			for br in cond.get_branches():
				br.compute_probability(total)

	"""
			sets the type of each condition based on "if/while/for/?" and other
		keywords found in condition text
	"""
	def establish_conditions_type(self):
		for cond in self.conditions:
			cond.establish_type()

	"""
			reiterates through all conditions and detects multiple conditions
			TODO: detect using /*MULTICOND*/ flag
	"""
	def establish_conditions_type_leveltwo(self):
		""" Here we will retag the Unknown resulted from multiple if conds
			We will get through all conditions and see if one of them is
			ending or starting with	&& or ||
		"""
		for i in range(len(self.conditions)-1):
			currentCond = self.conditions[i]
			nextCond = self.conditions[i+1]
			testCurrentCond = currentCond.get_test()#.strip().rstrip()
			testNextCond = nextCond.get_test()#.strip().rstrip()

			if currentCond.type != "UNKNOWN" and nextCond.type == "UNKNOWN" and\
			   ( testCurrentCond.endswith("&&") or testCurrentCond.endswith("||") or\
			   	 testNextCond.startswith("&&") or testNextCond.startswith("||") ):
				nextCond.type = currentCond.type
				currentCond.set_multicond()
				nextCond.set_multicond()

class Classifier:
	"""
			Conditions are classified by type or
		by Expectations and printed when it's needed
	"""
	def __init__(self, conds):
		self.allConds = conds
		self.ifConds = []
		self.whileConds = []
		self.forConds = []
		self.unknownConds = []
		self.macroConds = []
	def classify_expected(self):
		for cond in self.allConds:
			if constants.Constants.UNLIKELY != None and\
				  len(constants.Constants.UNLIKELY) > 0 and\
				  any(word in cond.get_test() for word in constants.Constants.UNLIKELY):
				cond.expected = constants.Constants.UNEXPECTED
			elif constants.Constants.LIKELY != None and\
				len(constants.Constants.LIKELY) > 0 and\
				any(word in cond.get_test() for word in constants.Constants.LIKELY):
				cond.expected = constants.Constants.EXPECTED
			else:
				cond.expected = constants.Constants.NONE

	def classify_type(self):
		for cond in self.allConds:
			if cond.type == constants.Constants.IF:
				self.ifConds.append(cond)
			elif cond.type == constants.Constants.WHILE:
				self.whileConds.append(cond)
			elif cond.type == constants.Constants.FOR:
				self.forConds.append(cond)
			elif cond.type == "MACRO":
				self.macroConds.append(cond)
			else:
				self.unknownConds.append(cond)
	def print_cc(self):
		print "\n\n-=- IF Conditions -=-\n\n"
		print_conds(self.ifConds)
		print "\n\n-=- WHILE Conditions -=-\n\n"
		print_conds(self.whileConds)
		print "\n\n-=- FOR Conditions -=-\n\n"
		print_conds(self.forConds)
		print "\n\n-=- MACRO Conditions -=-\n\n"
		print_conds(self.macroConds)
		print "\n\n-=- Unknown Conditions -=-\n\n"
		print_conds(self.unknownConds)


class Logger:
	"""
		Output files are created and filled with information
	"""
	def __init__(self, execConds, neverConds, filenameCSV, filenameRAW):
		self.execConditions = execConds
		self.neverConditions = neverConds
		self.csvFilename = filenameCSV
		self.rawFilename = filenameRAW
		self.csvFile = None
		self.rawFile = None

	def create_log_files(self):
		try:
			self.csvFile = open(self.csvFilename, 'w')
			self.rawFile = open(self.rawFilename, 'w')
		except:
			print "Unexpected file opening error:",sys.exec_info()[0]
			raise

	def start(self):
		#print str(len(self.execConditions))+ " - " + str(len(self.neverConditions))
		self.write_csv()
		self.write_raw()

	def write_csv(self):
		try:
			""" writes all the conditions with no more than 2 branches
			    in the csvFile in the following format:
				tuples of: line #, taken, branch0_taken, branch1_taken, expected, multiple
				where:	taken is % of how many times branch was taken
						expected: 0 - contition is EXPECTED to happend
							 	  1 - condition is UNEXPECTED to happend
							      2 - unknown expectation

			"""
			s = "line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n"
			self.csvFile.write(s)
			for cond in self.execConditions :
				lista = cond.get_branches_times_executed()
				#print lista[0]
				if "branch ||" in cond.test:
					line = str(cond.line) + ", " \
                           + str(round((100.0 - cond.get_branches()[0].get_probability()),2)) + ", "  \
                           + str(lista[1]) + ", "  \
                           + str(lista[0]) + ", " \
                           + cond.expected + ", " \
                           + str(cond.num_branches) + ", " \
                           + cond.type + ", " \
                           + get_line_no(cond.test) + ", "\
						   +  cond.test + "\n"
					#print get_line_no(cond.test)
				else:
					line = str(cond.line) + ", " \
                           + str(round(cond.get_branches()[0].get_probability(),2)) + ", "  \
                           + str(lista[0]) + ", "  \
                           + str(lista[1]) + ", " \
                           + cond.expected + ", " \
                           + str(cond.num_branches) + ", " \
                           + cond.type + ", " \
                           + get_line_no(cond.test) + ", "\
						   +  cond.test + "\n"
					#print get_line_no(cond.test)
				self.csvFile.write(line)

		except:
			print "Unexpected file writing error"
			raise

		try:
			self.csvFile.close()
		except:
			print "Error on closing file"
			raise

		#print "Done writing in " + self.csvFilename + " ..."

	def write_raw(self):
		try:
			""" writes each condition in the rawFile in the following format
				Filename(line x):
					Condition: condition text
					Type: type of condition(IF,WHILE ...)
					#Branches: Number of branches in condition
					Multicond: 0 - not a part of a multiple condition
							   1 - a part of a multiple condition
					Expected: 0 - contition is EXPECTED to happend
							  1 - condition is UNEXPECTED to happend
							  2 - unknown expectation
					Branches:
							# : branch name - probability% (x times executed)
			"""
			for cond in self.execConditions :
				out = cond.to_string()
				self.rawFile.write(out)

			self.rawFile.write("\n\n---- Never Executed ----\n\n")
			for cond in self.neverConditions :
				out = cond.to_string()
				self.rawFile.write(out)
		except:
			print "Unexpected file writing error:",sys.exec_info()[0]
			raise

		try:
			self.rawFile.close()
		except:
			print "Error on closing file"
			raise

		#print "Done writing in " + self.rawFilename + " ..."

def print_conds(cond):
	for c in cond:
		#if c.num_branches <= 2:
		c.print_condition()



#if __name__ == "__main__" :
#applyOnFolder(sys.argv[1])
