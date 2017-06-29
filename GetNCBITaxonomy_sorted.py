#! /usr/bin/env python

import argparse
import sys
import os

BATCHSIZE = 100000
INDEXSIZE = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Taxonomy assignment script", version="1.0")
    parser.add_argument("-n", "--names", dest="names", metavar="NCBINames", type=str, help="NCBI names dump file.", required=True)
    parser.add_argument("-s", "--nodes", dest="nodes", metavar="NCBINodes", type=str, help="NCBI nodes dump file.", required=True)
    parser.add_argument("-g", "--giToTax", dest="gitax", metavar="NCBIGITax", type=str, help="NCBI GI to Taxonomy dump file.", required=True)
    parser.add_argument("-x", "--giToTaxIdx", dest="gitaxidx", metavar="NCBIGITaxIdx", type=str, help="NCBI GI to Taxonomy dump index file (for output).", required=True)
    parser.add_argument("-i", "--input", dest="input", metavar="inputFile", type=str, help="The input file with GIs.", required=True)
    parser.add_argument("-o", "--output", dest="output", metavar="outputFile", type=str, help="The output filename.", required=False, default="out")
    args = parser.parse_args()
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
            nameString = taxid_to_name[taxid]+";"+nameString
            (taxid,level) = parentDict[taxid]
            nameString = level+"="+nameString
        except KeyError as e:
            nameString += "NotRoot=NotRoot;"+nameString
            return nameString
    return nameString

## Define a function to return the path to the root a list of nodes
def parseToRootList(taxids, taxid_to_name, parentDict):
    """This function runs the parseToRoot function for every
    taxid in the list of taxids, and returns the list of strings
    with path for each taxid to the root."""
    nameStrings = [parseToRoot(x,taxid_to_name,parentDict) for x in taxids]
    return(nameStrings)

## First, make a dict of name and taxid
taxid_to_name = {}
namesf = open(args.names)
for line in namesf:
    toks = line.strip().split("\t")
    taxid_to_name[int(toks[0])] = toks[2]
print "Done loading Taxid to name data."
namesf.close()
    
## Second, load the parent dict.
parentDict = {}
nodesf = open(args.nodes)
for line in nodesf:
    toks = line.strip().split("\t")
    parentDict[int(toks[0])] = (int(toks[2]), toks[4])
print "Done load parent data."
nodesf.close()

## Lastly, make a dictionary to convert GI to taxid 
## Test that the index file exists, if not,
## make it. You should never read the gi to taxid file 
## since it is going to be incredibly big and impossible
## to store in memory.
gi_to_taxid_index = []
if not os.path.isfile(args.gitaxidx):
    INDEXSIZE=10000
    cnt = 0
    gitaxidxf = open(args.gitaxidx, "w")
    gi_to_taxid_index.append(0)
    gitaxidxf.write(str(INDEXSIZE)+"\n")
    gitaxidxf.write("0\n")
    gitaxf = open(args.gitax)
    oldGI = 0
    oldGIIdx = 0
    while True:
        line = gitaxf.readline()
        if line == "": break
        toks = [ int(x) for x in line.strip().split() ]
        if len(toks) != 2:
            print "GI to taxid dmp file has a misformed line:", line
            sys.exit(2)
        if toks[0] <= oldGI:
            print "GI to taxid dmp is not sorted, so please run it without the -s(orted) option."
            print "The unsorted version is super slow - take that into consideration."
            sys.exit(1)
        oldGI = toks[0]
        curGIIdx = int(toks[0]/INDEXSIZE)
        if curGIIdx > oldGIIdx:
            tempcount = (curGIIdx - oldGIIdx)
            curtell = gitaxf.tell() - len(line)
            while tempcount > 0:
                tempcount -= 1
                gi_to_taxid_index.append(curtell)
                gitaxidxf.write(str(curtell)+"\n")
            oldGIIdx = curGIIdx
        cnt += 1
        if (cnt%INDEXSIZE == 0):
            print cnt, "lines done.\r",
            sys.stdout.flush()
    gitaxf.close()
    gitaxidxf.close()
    print "Generated and loaded index file for gi to taxid dmp file."
else:
    gitaxidxf = open(args.gitaxidx, "r")
    INDEXSIZE = int(gitaxidxf.readline().strip())
    for line in gitaxidxf:
        toks = [int(x) for x in line.strip().split()]
        if len(toks) != 1:
            print "Index file has incorrect format for line:", line
            sys.exit(3)
        gi_to_taxid_index.append(toks[0])
    gitaxidxf.close()
    print "Loaded index file for gi to taxid dmp file."

## Read the list of gis that are input
GIf = open(args.input)
gitaxf = open(args.gitax)
outf = open(args.output, "w")
cnt = 0
oldIndex = 0
oldGI = 0
for line in GIf:
    toks = line.strip().split()
    if len(toks) != 1: 
        print "Ignoring line with incorrect format:", line
        continue
    curGI = int(toks[0])
    ### Given that you have the indexsize
    ### the last GI with value less than 
    ### our given GI is just the element 
    ### int(givenGI/indexsize)
    curIndex = int(curGI/INDEXSIZE)
    if curIndex != oldIndex: 
        ## different partof file, so go 
        ## to that partof the the gi-to-taxid 
        ## file
        oldIndex = curIndex
        gitaxf.seek(gi_to_taxid_index[curIndex], 0)
    elif curGI < oldGI:
        ## same partof file, but since gi-to-taxid
        ## is sorted, we have jumped over that, so
        ## go back to the start of this block.
        gitaxf.seek(gi_to_taxid_index[curIndex], 0)
    ## If neither of the above 2 options, start reading the Gitax
    ## file till you find our gi, or go to the index of the gi 
    ## in the gitax file is greater than our curIndex, in which
    ## case we do not have that gi in our db. 
    for gine in gitaxf:
        (gi, tax) = [int(x) for x in gine.strip().split()]
        if int(gi/INDEXSIZE) != curIndex:
            print "Cannot find the GI", curGI, "in the gi to taxonomy file."
            continue
        if curGI == gi: 
            nameString = parseToRoot(tax, taxid_to_name, parentDict)
            outf.write(str(gi)+"\t"+nameString+"\n")
            break
    cnt += 1
    if (cnt%BATCHSIZE == 0): 
        print cnt, "GIs processed from input."
GIf.close()
gitaxf.close()
outf.close()


