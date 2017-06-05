#! /usr/bin/env python

import argparse
import sys
import os

BATCHSIZE = 100000

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Taxonomy assignment script", version="1.0")
    parser.add_argument("-n", "--names", dest="names", metavar="NCBINames", type=str, help="NCBI names dump file.", required=False, default="")
    parser.add_argument("-s", "--nodes", dest="nodes", metavar="NCBINodes", type=str, help="NCBI nodes dump file.", required=False, default="")
    parser.add_argument("-g", "--giToTax", dest="gitax", metavar="NCBIGITax", type=str, help="NCBI GI to Taxonomy dump file.", required=False, default="")
    parser.add_argument("-i", "--input", dest="input", metavar="inputFile", type=str, help="The input file with GIs.", required=True)
    parser.add_argument("-o", "--output", dest="output", metavar="outputFile", type=str, help="The output filename.", required=False, default="out")
    args = parser.parse_args()
    if args.names == "" or args.nodes == "" or args.gitax == "":
        print "You need to give the three NCBI dump file names and the index output file as input."
        sys.exit(1)
    if os.path.isfile(args.output):
        print "Output file", args.output, "already exists. Please delete it if you want to write over it."
        sys.exit(2)


## Define a function to return the path to the root for this 
## node.
def parseToRoot(taxid, taxid_to_name, parentDict):
    """This function takes a single taxid (integer),
    processes it to get the path to the root for that 
    taxid, returning the list of names of the different
    nodes."""
    nameString = ""
    while (taxid != 1):
        try:
            nameString += taxid_to_name[taxid]
            taxid = parentDict[taxid]
        except KeyError as e:
            nameSting += ";NotRoot"
            return nameString
    return nameString

## Define a function to return the path to the root a list of nodes
def parseToRootList(taxids, taxid_to_name, parentDict):
    """This function runs the parseToRoot function for every
    taxid in the list of taxids, and returns the list of strings
    with path for each taxid to the root."""
    nameStrings = [parseToRoot(x,taxid_to_name,parent_dict) for x in taxids]
    return(nameStrings)

## First, make a dict of name and taxid
taxid_to_name = {}
namesf = open(args.names)
for line in namesf:
    toks = line.strip().split()
    taxid_to_name[int(toks[0])] = toks[2]
print "Done loading Taxid to name data."
namesf.close()
    
## Second, load the parent dict.
parentDict = {}
nodesf = open(args.nodes)
for line in nodesf:
    toks = line.strip().split()
    parentDict[int(toks[0])] = int(toks[2])
print "Done load parent data."
nodesf.close()

## Read the list of gis that are input
inputGIs = []
GIf = open(args.input)
cnt = 0
for line in GIf:
    inputGIs.append(line.strip())
    cnt += 1
    if (cnt%BATCHSIZE == 0): 
        print cnt, "GIs read from input."
GIf.close()

## Lastly, make a dictionary to convert GI to taxid 
## Test that the index file exists, if not,
## make it. You should never read the gi to taxid file 
## since it is going to be incredibly big and impossible
## to store in memory.
gi_to_taxid_index = {}
for line in gitaxf:
    toks = [ int(x) for x in line.strip().split() ]
    if int(toks[0]/WINDOW) > curTokWin:
        print cnt, "lines done."
        curTokWin = int(toks[0]/WINDOW)
        gi_to_taxid_index[curTokWin*WINDOW] = gitaxf.tell() - len(line)
        gitaxidxf.write(str(curTokWin*WINDOW)+"\t"+str(gi_to_taxid_index[curTokWin*WINDOW])+"\n")
    cnt += 1
gitaxf.close()
gitaxidxf.close()

