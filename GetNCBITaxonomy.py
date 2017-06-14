#! /usr/bin/env python

import argparse
import sys
import os

BATCHSIZE = 10000

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Taxonomy assignment script", version="1.0")
    parser.add_argument("-n", "--names", dest="names", metavar="NCBINames", type=str, help="NCBI names dump file.", required=True)
    parser.add_argument("-s", "--nodes", dest="nodes", metavar="NCBINodes", type=str, help="NCBI nodes dump file.", required=True)
    parser.add_argument("-g", "--giToTax", dest="gitax", metavar="NCBIGITax", type=str, help="NCBI GI to Taxonomy dump file.", required=True)
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
    toks = line.strip().split()
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

## Read the list of gis that are input
inputGIs = []
GIf = open(args.input)
cnt = 0
for line in GIf:
    toks = line.strip().split()
    if not toks: continue
    inputGIs.append(int(toks[0]))
    cnt += 1
    if (cnt%BATCHSIZE == 0): 
        print cnt, "GIs read from input."
GIf.close()
print len(inputGIs), "loaded from input file."
totGIs = len(inputGIs)

## Lastly, read the gi_to_taxid file and
## at the same time parse through the list
## of gis to make a temporary list of taxids 
## for the gis found in the file until now.
## Once this list reaches batch size, get paths
## for this temporary list, while deleting
## these gis from the original list, and 
## keep going till no gis are left in our
## original list or we reach end of gi_to_taxid
## file.
gitaxf = open(args.gitax)
outf = open(args.output, "w")
temp_gis = []
temp_taxids = []
cnt = 0
lns = 0
for line in gitaxf:
    (gi,taxid) = [int(x) for x in line.strip().split()]
    lns += 1
    if lns % 1000000 == 0:
        print lns, "lines processed."
    if gi in inputGIs:
        temp_taxids.append(int(taxid))
        temp_gis.append(gi)
        cnt += 1
        if cnt == totGIs: break
        if (cnt % BATCHSIZE) == 0:
            nameStrings = parseToRootList(temp_taxids, taxid_to_name, parentDict)
            for (cgi, namestring) in zip(temp_gis, nameStrings):
                outf.write(cgi+"\t"+namestring+"\n")
            del nameStrings
            del temp_gis[:]
            del temp_taxids[:]
            print cnt, "gis in input processed."
print len(temp_taxids)
if temp_taxids:
    nameStrings = parseToRootList(temp_taxids, taxid_to_name, parentDict)
    for (cgi, namestring) in zip(temp_gis, nameStrings):
        outf.write(str(cgi)+"\t"+namestring+"\n")
    del nameStrings
    del temp_gis[:]
    del temp_taxids[:]
gitaxf.close()
outf.close()
