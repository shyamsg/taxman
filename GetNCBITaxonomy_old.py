#! /usr/bin/env python

import argparse
import pickle
import sys
import os

WINDOW = 100000

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Taxonomy assignment script", version="1.0")
    parser.add_argument("-p", "--pickledVerion", dest="pickled", metavar="NCBIPickle", type=str, help="The path of the pickle file with the NCBI names, nodes and index to the GI to tax dumps.", required=False, default="")
    parser.add_argument("-n", "--names", dest="names", metavar="NCBINames", type=str, help="NCBI names dump file.", required=False, default="")
    parser.add_argument("-s", "--nodes", dest="nodes", metavar="NCBINodes", type=str, help="NCBI nodes dump file.", required=False, default="")
    parser.add_argument("-g", "--giToTax", dest="gitax", metavar="NCBIGITax", type=str, help="NCBI GI to Taxonomy dump file.", required=False, default="")
    parser.add_argument("-x", "--giToTaxIdx", dest="gitaxidx", metavar="NCBIGITaxIdx", type=str, help="NCBI GI to Taxonomy dump index file (for output).", required=False, default="")
    parser.add_argument("-i", "--input", dest="input", metavar="inputFile", type=str, help="The input file with GIs.", required=True)
    parser.add_argument("-o", "--output", dest="output", metavar="outputFile", type=str, help="The output filename.", required=False, default="out")
    args = parser.parse_args()
    if args.pickled == "": 
        if args.names == "" or args.nodes == "" or args.gitax == "" or args.gitaxidx == "":
            print "You need to give the three NCBI dump file names and the index output file or the pickled file name as input."
            sys.exit(1)
    else:
        if args.names != "" or args.nodes != "" or args.gitax != "" or args.gitaxidx != "":
            print "Since the pickled option is provided, the options 'names', 'nodes', 'gitax' and 'gitaxidx' will be ignored."

    if os.path.isfile(args.output):
        print "Output file", args.output, "already exists. Please delete it if you want to write over it."
        sys.exit(2)

if args.pickled == "":
    
    ## process the files and then pickle them
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

    ## Lastly, make a dictionary to convert GI to taxid 
    ## Test that the index file exists, if not,
    ## make it. You should never read the gi to taxid file 
    ## since it is going to be incredibly big and impossible
    ## to store in memory.
    gi_to_taxid_index = {}
    if not os.path.isfile(args.gitaxidx):
        cnt = 0
        gitaxidxf = open(args.gitaxidx, "w")
        gi_to_taxid_index[0] = 0
        gitaxidxf.write("0\t0\n")
        gitaxf = open(args.gitax)
        curTokWin = 0
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
    else:
        gitaxidxf = open(args.gitaxidx, "r")
        for line in gitaxidxf:
            toks = [int(x) for x in line.strip().split()]
            gi_to_taxid_index[toks[0]] = toks[1]
        gitaxidxf.close()
    ## Pickle it!
    pickf = open(args.output+".taxonomy.pickle", "wb")
    pickle.dump((gi_to_taxid_index, taxid_to_name, parentDict), pickf, pickle.HIGHEST_PROTOCOL)
    pickf.close()
else:
    ## This will load the dilled versions
    pickf = open(args.pickled)
    pickle.load(pickf)
    pickf.close()
    print "Loaded the three dictionaries."

