import sys
import logging
from optparse import OptionParser
from lib.BaitDesc import BaitDesc

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__=="__main__":
	parser = OptionParser(usage="usage: %prog [-i input_templ.msdesc] [-b NN] [-t NN] [-o fileout.fa]")
	parser.add_option("-i", "--input", dest="temp_in", help="Input template file, otherwise it will read from the stardard input.")
	parser.add_option("-b", "--bottomlimit", dest="lowlim", help="Bottom limit (in bp) for the microsatellite length. [default 10]")
	parser.add_option("-t", "--toplimit", dest="highlim", help="Top limit (in bp) for the microsatellite length. [default 35]")
	parser.add_option("-o", "--output", dest="fafile", help="File output (FastaA file). If not specified standard output will be used.")

	(options, args) = parser.parse_args()

	lowlim=10
	highlim=35
	if options.lowlim: lowlim=int(options.lowlim)
	if options.highlim: highlim=int(options.highlim)

	if lowlim>=highlim: parser.error("Bottom limit cannot be higher than top limit.")

	fin=sys.stdin
	if options.temp_in: fin=open(options.temp_in)
	else: sys.stderr.write("Reading from <stdin>, ctrl+c to interrupt (execute with --help for more info)\n")

	fout=sys.stdout
	if options.fafile:
		if not options.fafile.lower().endswith(".fa"): options.fafile+=".fa"
		fout=open(options.fafile,"w")

	try:
		bd=BaitDesc(fin)
	except KeyboardInterrupt as e:
		print "Cancelling..."
		sys.exit(-1)

	bd.generatelist(lowlim,highlim,fout)

	fin.close()
	fout.close()

