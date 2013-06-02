#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

import sys
import logging
from lib.BaitDesc import BaitDesc
import argparse

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__=="__main__":

	USAGE=''' Reads a .msdesc file (MS description file) and generates a FastA file containing
all the baits according to the specified parameters'''

	parser = argparse.ArgumentParser(usage=USAGE)
	parser.add_argument("-i", dest="input",help="Input MS description file. [.msdesc]",required=True)
	parser.add_argument("-b", dest="bottomlimit",help="Bottom limit (in bp) for the microsatellite length. [10]",default=10,type=int)
	parser.add_argument("-t", dest="toplimit",help="Top limit (in bp) for the microsatellite length. [35]",default=35,type=int)
	parser.add_argument("-o", dest="output",help="File output (FastaA file). If not specified [out-baits.fa] will be used",default="out-baits.fa")
	args = parser.parse_args()

	if args.bottomlimit>=args.toplimit: parser.error("Bottom limit cannot be higher than top limit.")

	fin=open(args.input)
	fout=open(args.output,"w")

	try:
		bd=BaitDesc(fin)
	except KeyboardInterrupt as e:
		print "Cancelling..."
		sys.exit(-1)

	bd.generatelist(args.bottomlimit,args.toplimit,fout)

	fin.close()
	fout.close()
	logging.info( " *** [ {0} ] *** WRITTEN!".format(args.output))
