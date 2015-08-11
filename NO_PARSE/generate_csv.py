#!/usr/bin/env python
import os
import sys
import calculs
import constants
filename = ""
#filename = "/home/GabrielCSMO/Documents/all_folders/folder_zend_hash.c/zend_hash.c.gcov"
interestingConds = []
csvOutput = "" #filename[:-5] + ".csv" #/home/GabrielCSMO/Documents/all_folders/folder_zend_hash.c/zend_hash.csv"
rawOutput = "" #filename[:-5] + ".output"#"/home/GabrielCSMO/Documents/all_folders/folder_zend_hash.c/zend_hash.output"
#os.system("python compile_zend.py")


print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)


def applyOnFolder(target):
	
	old_path = os.getcwd()
	os.chdir(target)
	print os.getcwd()
	dir_ls = os.listdir(".")
	for item in dir_ls:
		if os.path.isdir(item):
			applyOnFolder(target + "/" + item)
		elif item.endswith(".gcov"):
			generate(item)
	os.chdir(old_path)


def generate(fname):

	global filename, rawOutput, csvOutput
	if len(fname)  <= 0 or fname == None:
		print "You must give filename parameter"
		exit()

	filename = fname
	csvOutput = fname[:-5] + ".csv" #/home/GabrielCSMO/Documents/all_folders/folder_zend_hash.c/zend_hash.csv"
	rawOutput = fname[:-5] + ".output"#"/home/GabrielCSMO/Documents/all_folders/folder_zend_hash.c/zend_hash.output"

	parser = Parser(filename)
	parser.start()

	"""We have all the conditions in text in parser.conds list"""
	conds = parser.conditii

	#printConds(parser.conditii)

	filtru = Filter(conds)
	filtru.removeNonBranch()
	filtru.removeCall()
	filtru.removeNeverExecuted()
	filtru.compute()

	cc = Classifier(filtru.interestingConds)
	cc.classifyExpected()

	log = Logger(filtru.interestingConds, filtru.onlyNeverExecuted, csvOutput, rawOutput)
	log.createLogFiles()
	log.start()


	nrI = len(filtru.interestingConds) 
	nrN	= len(filtru.onlyNeverExecuted)
	total = nrN + nrI
	if total != 0 :
		pI = round(nrI * 100.0 / total, 2)
		pN = round(nrN * 100.0 / total, 2)
	else:
		pI = pN = 0
	print "\n\nStatistics:\n\tExecuted: " + str(pI) + "% (" + str(nrI) + " conditions)"
	print "\tNever Executed: " + str(pN) + "% (" + str(nrN) + " conditions)"



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

	def setName(self, nume):
		self.name = nume

	def getName(self):
		return self.name

	def getProbability(self):
		return self.probability

	def getTimesExecuted(self):
		return self.timesExecuted

	def extractTimesExecuted(self):
		lista = self.name.split("taken")
		self.setName(lista[0].strip())
		timesExec = lista[1].strip().split(" ")
		self.timesExecuted = int(timesExec[0])


		""" here we extract the number of each branch """
		alls = lista[0].split(" ")
		self.number = alls[len(alls)-2]
		#print int(timesExec[0])

	def computeProbability(self, nr):
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
		self.type = constants.UNKNOWN
		self.multiCond = 0
		self.num_branches = 0
		self.expected = 2 # 0 - EXPECTED ; 1 - UNEXPECTED ; 2 - UNKNOWN

	def copyCondition(self, cond):
		self.test = cond.test
		self.line =	cond.line
		self.branches = cond.branches

	def setTest(self, test):
		self.test = test

	def setMultiCond(self):
		self.multiCond = 1

	def resetMultiCond(self):
		self.multiCond = 0

	def setLine(self,lineno):
		self.line = lineno

	def getBranches(self):
		return self.branches

	def addBranch(self,name, no, prob):
		self.branches.append(Branch(name,no,prob))
	
	def getTest(self):
		return self.test

	def computeSumBranches(self):
		for br in self.branches:
			if "unconditional" not in br.getName():
				self.num_branches +=1
				self.sumBranches += br.getTimesExecuted()

	def establishType(self):
		if "if branch" in self.test:
			self.type = constants.IF
		elif "while branch" in self.test:
			self.type = constants.WHILE
		elif "for branch" in self.test:
			self.type = constants.FOR
		elif "?" in self.test: #conditional expression - might have some issues on C++ code
			self.type = constants.IF

	def removeBranch(self, branch):
		self.branches.remove(branch)

	def getBranchesTimesExecuted(self):
		lista = []
		for br in self.branches:
			if "unconditional" not in br.getName():
				lista.append(br.getTimesExecuted())
		return lista
			
	def toString(self):

		filen = filename.split("/")
		source_file = filen[len(filen) - 1][:-5]
		s = "\n" + source_file +"(line " + str(self.line) + "):\n\tCondition: " + self.test +\
		"\n\tType: " + self.type +\
		"\n\t#Branches: " + str(self.num_branches) +\
		"\n\tMulticond: " + str(self.multiCond) +\
		"\n\tExpected: " + str(self.expected) +\
		"\n\tBranches:"
		for br in self.branches :
			#print(" %i : %s - %.2f (%i times executed)")
			s += "\n\t\t" + str(br.number) + ": "+ br.name + " - " + str(round(br.probability,2)) + "% (" + str(br.getTimesExecuted()) +" times executed)"

		return s

	def printCondition(self):
		filen = filename.split("/")
		source_file = filen[len(filen) - 1][:-5]
		print "\n" + source_file +"(line " + str(self.line) + "):\n\tCondition: " + self.test
		print "\tType: " + self.type
		print "\t#Branches: " + str(self.num_branches)
		print "\tMulticond: " + str(self.multiCond)
		print "\tBranches:"
		for br in self.branches :
			#print(" %i : %s - %.2f (%i times executed)")
			print "\t\t" + str(br.number) + ": "+ br.name + " - " + str(round(br.probability,2)) + "% (" + str(br.getTimesExecuted()) +" times executed)"

	def getSumBranches(self):
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
		print "A parser for file " + self.path + " was created!"
		
	def start(self):
		print "Started to parse gcov file..."
		
		with open(self.path) as f:
			content = f.read().splitlines()

		for i in range(len(content)-1):
			
			if(content[i].startswith("unconditional") or content[i].startswith("branch") or content[i].startswith("call") ) and\
			  (content[i-1].startswith("unconditional") == False and content[i-1].startswith("branch") == False and content[i-1].startswith("call") == False ) :
				#print "Test line "+str(i)+":\n"
				"""Split the line to find out the line number where the branch/call occurs"""
				lista = content[i-1].split(":")
				lineno = lista[1].strip().rstrip()
				test = lista[2].strip().rstrip()
				self.sharedcond.setTest(test)
				self.sharedcond.setLine(lineno)

				#print content[i]
				self.sharedcond.addBranch(content[i],0,0)
				
				if content[i+1].startswith("unconditional") == False and content[i+1].startswith("branch") == False and content[i+1].startswith("call") == False :
					cond = Condition("",0)
					cond.copyCondition(self.sharedcond)
					self.conditii.append(cond)
					self.sharedcond.reset()
					#print "End test\n\n"	
			
			elif	(content[i].startswith("unconditional") or content[i].startswith("branch") or content[i].startswith("call") ) and\
			  		(content[i+1].startswith("unconditional") or content[i+1].startswith("branch") or content[i+1].startswith("call") ) :
				self.sharedcond.addBranch(content[i],0,0)
				#print content[i]
			
			elif	(content[i].startswith("unconditional") or content[i].startswith("branch") or content[i].startswith("call ") ) and\
			  		(content[i+1].startswith("unconditional") == False and content[i+1].startswith("branch") == False and content[i+1].startswith("call ") == False ) :
				#print content[i]
				self.sharedcond.addBranch(content[i],0,0)
				
				cond = Condition("",0)
				cond.copyCondition(self.sharedcond)
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
		print "Started to filter the conditions results..."
		
		# here we set conditions types (IF/WHERE/FOR)
		self.establishConditionsType()
		
		# reiterate through conditions to spot the multiple ones that were taged
		#initially as UNKNOWN
		#self.establishConditionsTypeLevel2()
	
	"""
			add to branchConds the subset of conditions that contains
		at least one branch
	"""
	def removeNonBranch(self):
		for cond in self.conditions:
			ok = 0
			branches = []
			for br in cond.branches:
				if "branch" in br.getName():
					ok = 1
			if ok == 1 :
				#print "got here"
				self.branchConds.append(cond)
		
	"""
		remove the each "call" considered condition branch
	"""
	def removeCall(self):
		for cond in self.branchConds:
			partialbr = []
			for br in cond.getBranches():
				text = br.getName()
				if text.startswith("call") == False and text.startswith("unconditional") == False :
					partialbr.append(br)
				elif text.startswith("call") == False and (text.startswith("unconditional") and cond.type == "WHILE"):
					partialbr.append(br) 
			cond.branches = partialbr
	
	"""
			separates the conditions that were never executed from
		those with times executed != 0
	"""	
	def removeNeverExecuted(self):
		for cond in self.branchConds:
			partialbr = []
			for br in cond.getBranches():
				text = br.getName()
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
 			for br in cond.getBranches():
				br.extractTimesExecuted()

			cond.computeSumBranches()
			total = cond.getSumBranches()
			""" computes the probability for each branch of actual condition """
			for br in cond.getBranches():
				br.computeProbability(total)

	"""
			sets the type of each condition based on "if/while/for/?" and other
		keywords found in condition text
	"""
	def establishConditionsType(self):
		for cond in self.conditions:
			cond.establishType()

	"""
			reiterates through all conditions and detects multiple conditions
			TODO: detect using /*MULTICOND*/ flag
	"""
	def establishConditionsTypeLevel2(self):
		""" Here we will retag the Unknown resulted from multiple if conds 
			We will get through all conditions and see if one of them is 
			ending or starting with	&& or || 
		"""
		for i in range(len(self.conditions)-1):
			currentCond = self.conditions[i]
			nextCond = self.conditions[i+1]
			testCurrentCond = currentCond.getTest()#.strip().rstrip()
			testNextCond = nextCond.getTest()#.strip().rstrip()

			if currentCond.type != "UNKNOWN" and nextCond.type == "UNKNOWN" and\
			   ( testCurrentCond.endswith("&&") or testCurrentCond.endswith("||") or\
			   	 testNextCond.startswith("&&") or testNextCond.startswith("||") ):
				nextCond.type = currentCond.type
				currentCond.setMultiCond()
				nextCond.setMultiCond()

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
	def classifyExpected(self):
		for cond in self.allConds:
			if "UNEXPECTED" in cond.getTest():
				cond.expected = constants.UNEXPECTED
			elif "EXPECTED" in cond.getTest():
				cond.expected = constants.EXPECTED
			else:
				cond.expected = constants.NONE

	def classifyType(self):
		for cond in self.allConds:
			if cond.type == constants.IF:
				self.ifConds.append(cond)
			elif cond.type == constants.WHILE:
				self.whileConds.append(cond)
			elif cond.type == constants.FOR:
				self.forConds.append(cond)
			elif cond.type == "MACRO":
				self.macroConds.append(cond)
			else:
				self.unknownConds.append(cond)
	def printCC(self):
		print "\n\n-=- IF Conditions -=-\n\n"
		printConds(self.ifConds)
		print "\n\n-=- WHILE Conditions -=-\n\n"
		printConds(self.whileConds)
		print "\n\n-=- FOR Conditions -=-\n\n"
		printConds(self.forConds)
		print "\n\n-=- MACRO Conditions -=-\n\n"
		printConds(self.macroConds)
		print "\n\n-=- Unknown Conditions -=-\n\n"
		printConds(self.unknownConds)


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

	def createLogFiles(self):
		try:
			self.csvFile = open(self.csvFilename, 'w')
			self.rawFile = open(self.rawFilename, 'w')
		except:
			print "Unexpected file opening error:",sys.exec_info()[0]
			raise

	def start(self):
		#print str(len(self.execConditions))+ " - " + str(len(self.neverConditions))
		self.writeCSV()
		self.writeRAW()

	def writeCSV(self):
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
				lista = cond.getBranchesTimesExecuted()
				#print lista[0]
				line = str(cond.line) + ", " + str(round(cond.getBranches()[0].getProbability(),2)) + ", "  + str(lista[0]) + ", "  + str(lista[1]) + ", " + cond.expected + ", " + str(cond.num_branches) + ", " + cond.type + ", " +  cond.test+"\n"
				self.csvFile.write(line)

		except:
			print "Unexpected file writing error"
			raise

		try:
			self.csvFile.close()
		except:
			print "Error on closing file"
			raise

		print "Done writing in " + self.csvFilename + " ..."

	def writeRAW(self):
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
				out = cond.toString()
				self.rawFile.write(out)

			self.rawFile.write("\n\n---- Never Executed ----\n\n")
			for cond in self.neverConditions :
				out = cond.toString()
				self.rawFile.write(out)
		except:
			print "Unexpected file writing error:",sys.exec_info()[0]
			raise

		try:
			self.rawFile.close()
		except:
			print "Error on closing file"
			raise		
		
		print "Done writing in " + self.rawFilename + " ..."

def printConds(cond):
	for c in cond:
		#if c.num_branches <= 2:
		c.printCondition()



#if __name__ == "__main__" :
#applyOnFolder(sys.argv[1])
