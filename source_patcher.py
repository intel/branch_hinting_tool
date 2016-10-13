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

import argparse
import sys
import csv
import os
import shutil
import re
import glob

GCOV_DIR = "GCOVS"
STATS_FILE = "stats.csv"

def exitWithMsg(message):
    print(message + "\n")
    exit(1)

def getCommandLineOptions():
    parser = argparse.ArgumentParser(description="Source Patcher for Branch Hinting Tool")

    parser.add_argument("targetDir", action="store", help="Target directory")
    parser.add_argument("--revert", action="store_true", default=False, help="Reverts files to their original state (if possible)")
    parser.add_argument("--nbFiles", action="store", default = 5, type=int, help="Number of files to patch (files will be patched in order from the hottest to the least hot)")
    parser.add_argument("--maxPatchedLines", action="store", default = -1, type=int, help="Number of lines to patch (-1 - all) per file. ex: 3 - will patch the 3 hottest lines from each file.")
    parser.add_argument("--minUsagePerc", action="store", default = 80, type=int, help="Branches that are taken/not taken less than this percentage value are ignored.")
    return parser.parse_args()

###----------------------------------------------------###
###---------------------REVERT-------------------------###
###----------------------------------------------------###

def revertDirectory(directory):
    dirListing = glob.glob(directory + "/*")

    for item in dirListing:
        print "Processing " + item

        if os.path.exists(item):
            if os.path.isdir(item):
                revertDirectory(item)
            elif item.endswith(".old"):
                fileName = item[:-4]
                completeOldFilePath = os.path.join(directory, item)
                completeFilePath = os.path.join(directory, fileName)

                if os.path.exists(item):
                    os.remove(item)

                os.rename(item, fileName)


###----------------------------------------------------###
###---------------------PATCH--------------------------###
###----------------------------------------------------###

PATH_IDX = 0
FILENAME_IDX = 1
LINE_IDX = 2
ORIG_LINE_IDX = 3
STATE_IDX = 4
CURRENT_HINT_IDX = 5
EXP_HINT_IDX = 6
TOTAL_CNT_IDX = 7
TAKEN_PERC_IDX = 8
TAKEN_CNT_IDX = 9
NOT_TAKEN_CNT_IDX = 10
NB_BRACHES_IDX = 11
BRANCH_TYPE_IDX = 12
CODE_IDX = 13

class FileEntry:
    pass

class BranchEntry:
    pass

def loadAndProcessStats(statsFilePath, options):
    reader = None
    statsEntries = []
    try:
        statsFile = open(statsFilePath, "rb")
        reader = csv.reader(statsFile)

        try:
            current = reader.next()
            current = reader.next()

            crtLine = 1

            while current != None:
                nbElements = len(current)
                if nbElements > CODE_IDX:
                    try:
                        filePath = current[PATH_IDX].strip()
                        fileName = current[FILENAME_IDX].strip()

                        entry = None

                        for crtEntry in statsEntries:
                            if crtEntry.fileName == fileName and crtEntry.filePath == filePath:
                                entry = crtEntry
                                break

                        if entry == None:
                            entry = FileEntry()
                            entry.filePath = filePath
                            entry.fileName = fileName
                            entry.totalHits = 0
                            entry.branchEntries = []

                            statsEntries.append(entry)

                        branchType = current[BRANCH_TYPE_IDX].strip()
                        hintState = current[STATE_IDX].strip()
                        expHint = current[EXP_HINT_IDX].strip()
                        takenPercent = float(current[TAKEN_PERC_IDX].strip()) * 0.01
                        minTakenPercent = float(options.minUsagePerc) * 0.01

                        if branchType == "IF" and hintState == "MISSING" and expHint != "NONE" and (takenPercent >= minTakenPercent or takenPercent <= 1.0 - minTakenPercent):
                            branchEntry = BranchEntry()

                            branchEntry.line = int(current[LINE_IDX].strip())

                            origLine = current[ORIG_LINE_IDX].strip()

                            if origLine != "":
                                branchEntry.origLine = int(origLine)
                            else:
                                branchEntry.origLine = -1

                            branchEntry.state = current[STATE_IDX].strip()
                            branchEntry.crtHint = current[CURRENT_HINT_IDX].strip()
                            branchEntry.expHint = expHint
                            branchEntry.totalCount = int(current[TOTAL_CNT_IDX].strip())
                            branchEntry.takenPercent = takenPercent
                            branchEntry.takenCount = int(current[TOTAL_CNT_IDX].strip())
                            branchEntry.notTakenCount = int(current[NOT_TAKEN_CNT_IDX].strip())
                            branchEntry.nbBranches = int(current[NB_BRACHES_IDX].strip())

                            if nbElements > CODE_IDX + 1:
                                branchEntry.code = ",".join(current[CODE_IDX:nbElements])
                            else:
                                branchEntry.code = current[CODE_IDX]

                            entry.totalHits += branchEntry.totalCount
                            entry.branchEntries.append(branchEntry)
                    except:
                        print("Error parsing line %d: %s, skipped" % (crtLine, str(sys.exc_info()[1])))
                else:
                    print("Warning: incomplete line %d, ignored" % (crtLine))

                current = reader.next()
                crtLine += 1
        except StopIteration:
            pass

        statsFile.close()

    except:
        return None

    for entry in statsEntries:
        entry.branchEntries = sorted(entry.branchEntries, key=lambda entry: entry.totalCount, reverse=True)

    return sorted(statsEntries, key=lambda entry: entry.totalHits, reverse=True)


def revertFileFromFileEntry(fileEntry):
    filePath = os.path.join(fileEntry.filePath, fileEntry.fileName)
    os.remove(filePath)
    os.rename(filePath + ".old", filePath)


def fileHasBeenProcessed(fileEntry):
    return os.path.exists(os.path.join(fileEntry.filePath, fileEntry.fileName + ".old"))


def backupFile(fileEntry):
    sourceFile = os.path.join(fileEntry.filePath, fileEntry.fileName)
    targetFile = sourceFile + ".old"

    if os.path.exists(targetFile):
        os.remove(targetFile)

    shutil.copy(sourceFile, targetFile)


def hintExpression(hint, expression):
    if hint == "EXPECTED":
        return "EXPECTED(" + expression + ")"
    if hint == "UNEXPECTED":
        return "UNEXPECTED(" + expression + ")"
    return expression

ifExpr = re.compile("(if\s*\()")
singleLineCond = re.compile("(.*\?.*:.*)")
comment = re.compile("(/\*.*?\*/)")

def processLine(line, hint, lineNumber):

    if re.match(singleLineCond, line):
        print("Single line conditionals (expr ? valone : valtwo) not supported - line %d" % (lineNumber))
        return line

    #remove comments
    line = re.sub(comment, "", line)

    lineLen = len(line)
    ifMatch = re.search(ifExpr, line)

    exprStart = -1
    exprEnd = -1

    if ifMatch != None:
        for idx in range(ifMatch.end(0), lineLen):
            if line[idx].isspace() == False:
                    exprStart = idx
                    break
    else:
        for idx in range(0, lineLen):
            if line[idx].isspace() == False and line[idx] != '&' and line[idx] != '|':
                    exprStart = idx
                    break
    brackets = 0

    insideQuotes = False
    quotes = []

    for idx in range(exprStart, lineLen):
        if line[idx] == "\"" or line[idx] == "'":
            if insideQuotes == False:
                quotes.append(line[idx])
                insideQuotes = True
            else:
                if quotes[-1] == line[idx]:
                    quotes = quotes[:-1]

                    if len(quotes) == 0:
                        insideQuotes = False
                else:
                    quotes.append(line[idx])
        if insideQuotes == False:
            if line[idx] == "(":
                brackets += 1
            elif line[idx] == ")":
                brackets -= 1

                if brackets <= -1:
                    exprEnd = idx - 1
                    break

        if line[idx] == "\n":
            exprEnd = idx - 1
            break

    if brackets > 0:
        for idx in range(exprStart, exprEnd):
            if line[idx] == "(":
                brackets -= 1
                if brackets <= 0:
                    exprStart = idx + 1
                    break

    if exprStart == -1:
        print("Failed parsing line %d (could not find expr start)" % (lineNumber))
        return line

    if exprEnd == -1:
        print("Failed parsing line %d (could not find expr end)" % (lineNumber))
        return line

    expression = line[exprStart:exprEnd + 1].strip()

    line = line[0:exprStart] + hintExpression(hint, expression) + line[exprEnd + 1:lineLen]

    return line


def processFile(fileEntry, options):
    if fileHasBeenProcessed(fileEntry):
        revertFileFromFileEntry(fileEntry)

    backupFile(fileEntry)

    try:
        filePath = os.path.join(fileEntry.filePath, fileEntry.fileName)

        print ("Processing " + filePath)

        file = open(filePath, "rt")
        fileData = file.readlines()
        file.close()

        nbLinesToPatch = options.maxPatchedLines

        if nbLinesToPatch == -1:
            nbLinesToPatch = len(fileEntry.branchEntries)

        for branchEntry in fileEntry.branchEntries[:nbLinesToPatch]:
            currentLine = branchEntry.line - 1
            #print ("Before : " + fileData[currentLine])
            print ("Patching line %d with hit count %d taken %.2f%%" % (currentLine, branchEntry.totalCount, branchEntry.takenPercent * 100.0))
            fileData[currentLine] = processLine(fileData[currentLine], branchEntry.expHint, currentLine)
            #print ("After : " + fileData[currentLine])

        file = open(filePath, "wt")
        for line in fileData:
            file.write(line)
        file.close()

        print ("DONE " + filePath)
    except:
        print("Could not process file: " + filePath + " because " + str(sys.exc_info()[1]))


def patchDirectory(workingDir, options):

    absGCOVDir = os.path.join(workingDir, GCOV_DIR)

    if os.path.exists(absGCOVDir) == False:
        exitWithMsg("GCOV directory not found inside the target directory !")

    absStatsFilePath = os.path.join(absGCOVDir, STATS_FILE)

    if os.path.exists(absStatsFilePath) == False:
        exitWithMsg("Stats file not found inside the GCOV directory !")

    statsData = loadAndProcessStats(absStatsFilePath, options)

    if statsData == None:
        exitWithMsg("Failed to process stats file !")

    for entry in statsData[:options.nbFiles]:
        processFile(entry, options)

def main():
    options = getCommandLineOptions()

    absTargetDir = os.path.abspath(options.targetDir)

    if os.path.exists(absTargetDir) == False:
        exitWithMsg("Target directory not found !")

    if options.revert == True:
        revertDirectory(absTargetDir)
    else:
        patchDirectory(absTargetDir, options)

if __name__ == "__main__":
    main()
