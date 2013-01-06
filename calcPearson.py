#!/usr/bin/env python

import sys,os, getopt
import re
import csv
import itertools
from itertools import imap
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from HTMLParser import HTMLParser

# Get all the titles from the HTML files and return an array
def getdataTitles(htmlFiles):
	# Get all the dataTitles from the HTML documents
	# These dataTitles are what the raw data is about... for example, title 2002 is Population Growth Rate... 
	# We will use these dataTitles to open the files... 
	onlyfiles  = [ f for f in listdir(htmlFiles) if isfile(join(htmlFiles,f)) ]
	# Set the return array
	dataTitles = []
	# Populate dataTitles with these filenames...
	for i,files in enumerate(onlyfiles):
		#Open the File
		f = open(os.path.join(htmlFiles, files), "r+")
		theFile =  f.read()
		soup = BeautifulSoup(theFile)
		# # Parse the HTML HERE
		# Grab the TItle for this document
		try:
			title = soup.html.head.title
			title = re.sub('<[^<]+?>', '', str(title))
			title = title.split('::')[1][1:]
			dataTitles.append([re.sub('[^0-9]*', '', files), title])
		except (RuntimeError, TypeError, NameError, IndexError, AttributeError):
			print "ERROR: ", files
			pass
	dataToTsv(dataTitles, "stage1-titleNames");
	return dataTitles

def converRawData(dataTitles, rawDataFiles):
	# Set the return array
	selectedDataStats  = []
	countries = []
	# Search for All the countires in the Raw data files... 
	# Only include these 
	for i,fileNumber in enumerate(dataTitles):
		# Concatenate filename
		localFilename = "rawdata_" + fileNumber[0] + ".txt"
		# Try to open it
		f = open(os.path.join(rawDataFiles, localFilename), "r+")
		if(f):
			# If you found it... read the file
			theFile = f.read()
			# Split it into lines...
			for z,l in enumerate(theFile.split('\r')):
				# It's a TSV so sploit by tabs
				data = l.split('\t')
				if(len(data) > 2):
					# It's always in the 2nd column
					if any( data[1] in s for s in countries):
						pass
					else:
						countries.append(data[1])
			break
		else:
			# Couldn't find that sucker!
			print localFilename, " not found"

	# Now, let's add it to the selectedDataStats array
	selectedDataStats.append([])
	for country in countries:
		selectedDataStats[0].append(country)

	# Add all the data to the everything array
	for i,fileNumber in enumerate(dataTitles):
		# Concatenate filename
		localFilename = "rawdata_" + fileNumber[0] + ".txt"
		# Try to open it
		f = open(os.path.join(rawDataFiles, localFilename), "r+")
		if(f):
			# Read the fille
			theFile = f.read()
			# add a column to selectedDataStats
			selectedDataStats.append([])
			for country in countries:
				selectedDataStats[i + 1].append("")
			for z,l in enumerate(theFile.split('\r')):
				data = l.split('\t')
				if(len(data) > 2):
					for i6, country in enumerate(selectedDataStats[0]):
						if(country == data[1]):
							if(data[2] is None):
								selectedDataStats[i + 1][i6] = "!!!!"
							else:
								selectedDataStats[i + 1][i6] = data[2].replace(" ", "")
							break
		else:
			# Couldn't find that sucker!
			print localFilename, " not found"	
	dataToTsv(selectedDataStats, "stage2-allAvailableData");
	return selectedDataStats
	
def countData(selectedDataStats):
	# Set the Return Var
	counts             = [[],[]]

	# Count instances of the data... 
	for z in range(len(selectedDataStats[0])):
		count = 0
		for i8,line in enumerate(selectedDataStats): 
			if selectedDataStats[i8][z] is not "":
				count += 1
		counts[0].append(selectedDataStats[0][z])
		counts[1].append(count)
	# Sort all the Counts according to their number of counts
	counts[1], counts[0] = zip(*sorted(zip(counts[1], counts[0])))

	dataToTsv(counts, "stage3-dataCounts");
	return counts;

def getSelectedCountries(counts, requiredColumns):

	# Set the Return Var
	selectedCountries = []

	# For each contry determine if they have the minimun amount of data required
	# If so, add them to the new array
	for i9,count in enumerate(reversed(counts[0])):
		if counts[1][i9] >= requiredColumns:
			selectedCountries.append([counts[0][i9], counts[1][i9]])

	dataToTsv(selectedCountries, "stage4-selectedCountries");
	return selectedCountries

def getselectedDataStats(selectedCountries, dataTitles, rawDataFiles):

	# Set the Return Var
	selectedDataStats       = []
	selectedDataStatsTitles = []
	
	# Re-Add the data, if the country is in the selected countries
	selectedDataStats.append([])
	for country in selectedCountries:
		selectedDataStats[0].append(country[0])

	# Add all the data
	for i,fileNumber in enumerate(dataTitles):
		if(len(fileNumber) == 2):
			# Concatenate filename
			localFilename = "rawdata_" + fileNumber[0] + ".txt"
			# Try to open it
			f = open(os.path.join(rawDataFiles, localFilename), "r+")
			if(f):
				# Read the fille
				theFile = f.read()

				addToselectedDataStats = True
				selectedDataStatsTEMP  = []

				for country in selectedCountries:
					selectedDataStatsTEMP.append("")

				for z,l in enumerate(theFile.split('\r')):
					data = l.split('\t')
					if(len(data) > 2):
						for i6, country in enumerate(selectedDataStats[0]):
							if(country == data[1]):
								dataFigure = data[2].replace(" ", "")
								if(dataFigure is "" or dataFigure is None):
									addToselectedDataStats = False
									#print "EMPTY EMPTY EMPTY"
								else:
									selectedDataStatsTEMP[i6] = dataFigure
								break
				for w in selectedDataStatsTEMP: 
					if w == "":
						addToselectedDataStats = False
						break

				if(addToselectedDataStats == True and len(selectedDataStatsTEMP) == len(selectedDataStats[0])):
					selectedDataStats.append([])
					for i10, country in enumerate(selectedDataStats[0]):
						selectedDataStats[len(selectedDataStats)-1].append(selectedDataStatsTEMP[i10].replace('$','').replace(',',''))
					selectedDataStatsTitles.append([dataTitles[i][0],dataTitles[i][1]])
				else: 
					# print "NOT ADDED: ", dataTitles[i][0]
					pass

	# Rotate the array
	selectedDataStatsCountries = zip(*selectedDataStats)

	# Print how many statistics will be compared... 
	print "Selected Data: ",  len(selectedDataStatsTitles)

	# Start all to exports all statistics (This requires a different kind of Export...)
	dataToTsv(selectedDataStatsTitles, "stage5-selectedDataStatsTitles");
	dataToTsv(selectedDataStats, "stage5-selectedDataStats");
	dataToTsv(selectedDataStatsCountries, "stage5-selectedDataStatsCountries");

	return selectedDataStats, selectedDataStatsCountries, selectedDataStatsTitles

def calculateCorrelations(selectedDataStats, selectedDataStatsCountries, selectedDataStatsTitles): 

	# Open the file... 
	f3 = open("data/stage6-correlations.tsv", "w")

	# Write to the file all the statistics we have... 
	f3.write('\t') # The first column in the first row is empty
	for row in selectedDataStatsTitles:
		# print row[1]
		f3.write(row[1]) # This is the statistcTitle name... 
		f3.write('\t')
	f3.write('\n')

	# Start an Array
	correlations = []

	for index,row in enumerate(selectedDataStats[1:]): # Index 0 = country name... 

		subCorrelations = []

		# Add the title to the 
		f3.write(selectedDataStatsTitles[index][1]) # This is the statistcTitle name... 
		f3.write('\t')

		# We have to loop trhough selectedDataStats twice... calculate pearson for every row... 
		# Selected data should be 100% complete... no blank spaces...

		# We're going to populate this array
		# When this array is populated, we will compare all other rows to this array
		# One will be Perason = 1, since it will be the same...
		# This array, for example will have all the GDP figures for all counted countries 
		# 	and will compare them to, for example, Population growth...using Pearson...
		currentArray = [];
		for col in row:
			currentArray.append(float(col))

		for i,secondaryRow in enumerate(selectedDataStats[1:]):

			# This array is the comparrision array... 
			comparisonArray = []
			for col in secondaryRow:
				comparisonArray.append(float(col))

			# We are basically comparing 2 Arrays with perason and then writing the result
			correlation = str(pearsonr(currentArray, comparisonArray))
			subCorrelations.append(correlation)

			f3.write(correlation)
			f3.write('\t')

		correlations.append(subCorrelations)
		f3.write('\n')
	f3.close()

	# Write to File
	dataToTsv(correlations, "stage6-correlationsAlone");

	return correlations

def usage():

    print ' -------------------------------------------------------------------------'
    print ' Jorge Silva-Jetter (jorge.silva@thejsj.com) '
    print ' '
    print ' Ok, lets face it. No one is going to use this script except me....'
    print ' Properly documenting it is, at the moment, a waste of time..'
    print ' '
    print ' Typical usage:'
    # print ' KepInvestigationAtMAST.py --invid=GO10003 --quarter=1'
    print ' calcPearson.py --everything - Generete all data in TSV form'
    print ' calcPearson.py --remove     - Remove all data TSVs in data directory'
    print ' '
    #print ' --invid  Investigation ID number of GO program'
    #print ' --quarter  Kepler quarter (integer number)'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

def removeAllFilles():
	dataDirectory = os.getcwd() + "/data"
	for r,d,f in os.walk(dataDirectory):
		for fle in f:
			os.remove(os.path.join(dataDirectory,fle))
	print "All files deleted"

# Secondary Functions, used through out this script...
def average(x):
    assert len(x) > 0
    return float(sum(x)) / len(x)

def pearson_def(x, y):
    assert len(x) == len(y)
    n = len(x)
    assert n > 0
    avg_x = average(x)
    avg_y = average(y)
    diffprod = 0
    xdiff2 = 0
    ydiff2 = 0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff
    return diffprod / math.sqrt(xdiff2 * ydiff2)

def pearsonr(x, y):
  # Assume len(x) == len(y)
  n = len(x)
  sum_x = sum(x)
  sum_y = sum(y)
  sum_x_sq = sum(map(lambda x: pow(x, 2), x))
  sum_y_sq = sum(map(lambda x: pow(x, 2), y))
  psum = sum(imap(lambda x, y: x * y, x, y))
  num = psum - (sum_x * sum_y/n)
  den = pow((sum_x_sq - pow(sum_x, 2) / n) * 	(sum_y_sq - pow(sum_y, 2) / n), 0.5)
  if den == 0: return 0
  return num / den

def dataToTsv(array, filename):
	newFilename = open('data/' + filename + '.tsv', "w+")
	for row in array:
		for col in row: 
			newFilename.write(str(col))
			newFilename.write("\t")
		newFilename.write("\n")
	newFilename.close()
	print "		",filename, " Created"

def tsvToArray(filename, array):
	try:
		f = open("data/"+filename+".tsv", "r")
		for ii,line in enumerate(f.read().split("\n")):
			if(len(line.split("\t")) > 0):
				array.append([])
				for col in line.split("\t"):
					if(col != ""):
						array[ii].append(col.rstrip())
		return array
	except IOError as e:
		return False; 

def getselectedData(filename): 
	data = csv.reader(open('data/' + filename + '.tsv'), delimiter='\t')
	# Read the column names from the first line of the file
	selectedDataStats = []
	for i,row in enumerate(data):
		selectedDataStats.append([])
		for ii,col in enumerate(row):
			if(i == 0 or ii == 0):
				selectedDataStats[i].append(col)
			else:
				selectedDataStats[i].append(float(col))
			if(ii == len(row)-2):
				break
	return selectedDataStats

def everything():

	# Universals

	# 2 File Paths
	htmlFiles              = os.getcwd() + "/rankorder/html"
	rawDataFiles           = os.getcwd() + "/rankorder/rawdata"
	rawDataFilesWNames     = os.getcwd() + "/rankorder/rawdata-w-names"

	# Stage 1 - Get all titles for stats
	dataTitles             = []
	if(tsvToArray("stage1-titleNames", dataTitles) == False):
		dataTitles         = getdataTitles(htmlFiles)
	print "Stage 1 - Complete"

	# Stage 2 - Get all Countries in the factbook and all data
	selectedDataStats                = []
	if(tsvToArray("stage2-allAvailableData", selectedDataStats) == False):
		selectedDataStats            = converRawData(dataTitles, rawDataFiles) # A list of all the data in the CIA factbook
	print "Stage 2 - Complete"

	# Stage 3 - Count all Data... 
	counts                 = [[],[]]
	if(tsvToArray("stage3-dataCounts", counts) == False):
		counts             = countData(selectedDataStats)
	print "Stage 3 - Complete"

	# Stage 4 - Selected the countries that will be used in counting this data...
	selectedCountries      = []
	if(tsvToArray("stage4-selectedCountries", selectedCountries) == False):
		requiredColumns    = 80
		selectedCountries  = getSelectedCountries(counts, requiredColumns) # A list of coutnries with more than -requiredColumns-
	print "Stage 4 - Complete"

	# Stage 5 - Get Selected Data...
	selectedDataStatsStats      = []
	selectedDataStatsCountries  = []
	selectedDataStatsTitles     = []
	if(tsvToArray("stage5-selectedDataStats", selectedDataStats) == False or tsvToArray("stage5-selectedDataStatsTitles", selectedDataStatsTitles) == False):
			selectedDataStats, selectedDataStatsCountries, selectedDataStatsTitles = getselectedDataStats(selectedCountries, dataTitles, rawDataFiles) # List of all data columns, that all selectedCountries share... 
	print "Stage 5 - Complete"

	# Stage 6 - Calculate Correlations...
	finalCorrelations      = []
	if(tsvToArray("stage6-correlations.tsv", finalCorrelations) == False):
		finalCorrelations  = calculateCorrelations(selectedDataStats, selectedDataStatsCountries, selectedDataStatsTitles)
	print "Stage 6 - Complete"

	return finalCorrelations

def main():

    status = 0

# input arguments / KepInvestigationAtMAST.py --invid=STKL --quarter=1

    try:
    	opts, args = getopt.getopt(sys.argv[1:],"h:iq",["help","remove","everything","invid=","quarter="])
    except getopt.GetoptError:
    	usage()
    for o, a in opts:
	    if o in ("-h", "--help"):
	        usage()
	    if o in ("-r", "--remove"):
	        removeAllFilles()
	    if o in ("-e", "--everything"):
	        everything()
	    # Example Usage...
	    if o in ("-i", "--invid"):
        	invid = str(a)

# Do it
if __name__ == "__main__":
    main()