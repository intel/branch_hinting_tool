#!/usr/bin/env python

"""
DOES THE SUM OF 2 CSV FILES(ON 3RD AND 4TH
COLUMN BASED ON  EQUALITY ON 1ST COLUMN)
"""

import sys
import os
import collections
hmap = {}

class Merge():

	def __init__(self) :
		self.file = None
		self.map = {}

	def addFile(self, filename):
		
		try:
			self.file = open(filename , 'r')
		except:
			print "error while opening the files"
			raise


		content = self.file.read().splitlines()
		
		for i in range(len(content)) :
			if i == 0 :
				continue
			lista = content[i].split(", ")
			line = lista[0]
			proc = float(lista[1])
			b0 = int(lista[2])
			b1 = int(lista[3])
			mod_line = [proc, b0, b1, lista[4], lista[5], lista[6], lista[7]]

			if line not in self.map:
				self.map[line] = mod_line
			else: 
				self.map[line][1] += mod_line[1]
				self.map[line][2] += mod_line[2]
				self.map[line][0] = round( self.map[line][1] * 100.0 / (self.map[line][1] + self.map[line][2]), 2)
		
	def getMap(self):
		return self.map

	def writeToFile(self, filename):
		print filename +"\n"
  		wfile = None	
  		try:
  			wfile = open(filename, 'w')
  		except:
  			print self.filename + " - Write to file: error opening file for write\n"
  			raise
  		s = "line, taken, branch0_taken, branch1_taken, expected(0|1|2)\n"
		wfile.write(s)

		for key in self.map:
			#print str(key) + " - " + str(self.map[key])
			s = str(key) + ", " + str(self.map[key][0]) + ", " + str(self.map[key][1]) + ", " + str(self.map[key][2]) + ", " + str(self.map[key][3]) + ", " + str(self.map[key][4]) + ", " + str(self.map[key][5]) + ", " + str(self.map[key][6]) + "\n"
			wfile.write(s)

if 1 == 0 :
	m = Merge(sys.argv[1])
	m.openFile()
	m.start()
