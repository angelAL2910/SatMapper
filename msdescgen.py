#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

import gzip
import bz2
import sys
import tempfile
import logging
import argparse


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

class FastaFile():
	def __init__(self,fil):
		chf=fil
		extension=chf.split(".")[-1].lower()
		tempf=None
		self.chromosomes={}

		if extension in ['gz','bz2']: 
			tempf=tempfile.NamedTemporaryFile("w+")
			if extension=="gz":
				self.chf=gzip.GzipFile(chf)
			elif extension=="bz2":
				self.chf=bz2.BZ2File(chf)
		else: self.chf=open(fil)

		currentChromosome=None
		pos=0

		i=self.chf.readline()
		leni=0
		while i:
			if tempf: tempf.write(i)
			if i.startswith(">"): 
				currentChromosome=i[1:].strip()
				logging.info("Reading chromosome {0}...".format(currentChromosome))
				pos=0
				leni=0
			elif i.strip():
				if len(i)!=leni:
					leni=len(i)
					self.chromosomes.setdefault(currentChromosome,[]).append([pos,self.chf.tell()-len(i),leni,len(i.strip())])
				pos+=len(i.strip())
			i=self.chf.readline()

		if tempf:
			self.chf.close()
			self.chf=tempf


	def getChromosomes(self):
		return self.chromosomes.keys()

	def getLowPos(self,chrom,pos):
		for i in range(len(self.chromosomes[chrom])):
			if self.chromosomes[chrom][i][0]>pos: 
				i-=1
				break

		start,fpos,linelen,dnalen=self.chromosomes[chrom][i]

		jump=((pos-start)/dnalen)
		return jump*dnalen+start,jump*linelen+fpos

	def getChunk(self,chrom,pos,size):
		realpos,filepos=self.getLowPos(chrom,pos)
		vsize=size+pos-realpos
		self.chf.seek(filepos)
		data=""
		while True:
			l=self.chf.readline()
			if not l:break
			data+=l.strip()
			if len(data)>vsize: break
		return data[pos-realpos:pos-realpos+size]

	def close(self):
		self.chf.close()

class FormatFile():
	'''This class reads a MS template and allows access to each chromosome information by using []'''
	def __init__(self,formatfile):
		a=open(formatfile)
		chrid_to_n={}
		self.microsatellites={}
		for i in a:
			if not i.strip() or i.startswith("#"): continue
			i=i.strip().split("\t")
			try:
				chrn=int(i.pop(0))
				start=int(i.pop(0))
				end=int(i.pop(0))
				repeatsize=int(i.pop(0))
				fastaid="\t".join(i)
				chrid_to_n.setdefault(fastaid,chrn)
			except:
				raise Exception("Error in microsatellite description file (line {0}), invalid format.\nIt must be 6 tab separated fields.".format(j))

			if (end+1-start)%repeatsize:
				raise Exception("Error in microsatellite description file (line {0}).\nMicrosatellite length does not match with repeat length.".format(j))

			if chrid_to_n[fastaid]!=chrn:
				raise Exception("Error in microsatellite description file (line {0}).\nfastaID does not match with chromosome number.".format(j))

			self.microsatellites.setdefault(fastaid,[]).append((start,end,repeatsize,chrn))

	def __getitem__(self,chromosome):
		'''Everytime you access a chromosome the information is deleted
		One use only, this allows to save memory'''
		if chromosome in self.microsatellites:
			msslist=self.microsatellites[chromosome]
			del self.microsatellites[chromosome]
			return msslist
		return []

def patternDetect(cad,patlen):
	'''This method detects a tandem repeatd pattern in a string'''
	pattern=""
	for i in range(patlen):
		lettersatpos=cad[i::patlen]
		mostrepeated={}
		for i in lettersatpos:
			mostrepeated.setdefault(i,0)
			mostrepeated[i]+=1
		mostrepeated=[i[::-1] for i in mostrepeated.items()]
		mostrepeated.sort(reverse=True)
		pattern+=mostrepeated[0][1]
	
	return pattern


def mismatches(cad,patt):
	'''This method returns the number of mismatches in a string containgin tandem repeats given a pattern'''
	mm=0
	for i in range(len(cad)):
		if cad[i]!=patt[i%len(patt)]: mm+=1

	return mm

def processFraction(pattern,right):
	'''Returns the numbers of bases ocnteined in the fraction part of the MS'''
	i=0
	while True:
		if pattern[i%len(pattern)]==right[i]: i+=1
		else: break
	
	return i
	

def createBaits(chunk,armsize,start,end,repeatsize,chrn,output):
	'''Given a DNA string (chunk) armsze, astart and end positions in the chromosome, 
	repeatsize, chromosome number and output stream dumps the baits themselves'''

	left,right,ms=chunk[:armsize],chunk[-armsize:],chunk[armsize:-armsize]
	pattern=patternDetect(ms,repeatsize)

	if len(ms)%len(pattern):
		output.write( "# INDEL or INCORRECT SIZE : Chr {3}, Pos {4}, Pattern Length {5} : ...{0} | {1} | {2}...\n".format(left[-20:],ms,right[:20],chrn,start,repeatsize))
	elif mismatches(ms,pattern)>5:
		output.write( "# CHECK! >5 Mismatches	: Chr {3}, Pos {4}, Pattern Length {5} : ...{0} | {1} | {2}...\n".format(left[-20:],ms,right[:20],chrn,start,repeatsize))
	elif mismatches(ms,pattern):
		output.write( "# IMPURE MS <6 Mismatches : Chr {3}, Pos {4}, Pattern Length {5} : ...{0} | {1} | {2}...\n".format(left[-20:],ms,right[:20],chrn,start,repeatsize))
	else:
		output.write("# Ok!: ...{0} | {1} | {2}...\n".format(left[-20:],ms,right[:20]))
		
	fraction=processFraction(pattern,right)

	name="{0}_{1}_{2}".format(chrn,pattern,start)
	if fraction: name+=".{0}".format(fraction)

	armsize-=50

	output.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(name,pattern,left[-armsize:],right[fraction:][:armsize],ms))



if __name__=="__main__":
#	parser = OptionParser(usage="usage: %prog [-l ARMSLENGTH] <-t mss_spec_template.txt -o template.out f1.fa f2.fa.gz ...>")
#	parser.add_option("-t", "--template", dest="template", help="File containing the microsatellite specification list.")
#	parser.add_option("-o", "--output", dest="outfile", help="Specify file out either for template or the baits fasta. If it is not specified, stdout will be used.")
#	parser.add_option("-l", "--armlength", dest="armlength", help="Specify flanking sequence length (arms length) for the baits [100 by default].")
#	armlen=100

	USAGE='''
{0} reads a MS template file and generates the a MS specification
list. (.msdesc)

MS template files are TSV files (tab separated values) containing the following
fields:
	*	chromosome number
	*	start position
	*	end position
	*	pattern length
	*	fastA identifier in the reference genome

Given the template file path armlength and the FastA source files it will
generate a list of bait description in the following format (TSV):

	*	Locus : 		Auto generated name for the bait
	*	# chromosome: 		Chromosome number
	*	Pattern: 		Pattern detected
	*	Left flanking seq: 	Left flankind DNA sequence
	*	Right Flank Seq: 	Right flankind DNA sequence
	*	MS: 			MS found

Every bait description will be preceded by a comment/Log that will report if the
MS was found (Ok) or if it did not match with the template.

This software will generate a .msdesc file containing the MS specification list

Baits must be generated with baitsges.py providing a .msdesc file as input.
'''.format(sys.argv[0])

	parser = argparse.ArgumentParser(usage=USAGE)
	parser.add_argument("-t", dest="template",help="Template file",required=True)
	parser.add_argument("-l", dest="armlength",help="Specify arm lengths [100]",default=100,type=int)
	parser.add_argument("-o", dest="output",help="Output MS specification file [mss-out.msdesc]",default="mss-out.msdesc")
	parser.add_argument(dest="FASTAFILES",nargs='+',help="Fasta files containig chromosomes (gz and bz2 allowed but not recommended [SLOW])")
	args = parser.parse_args()

	armlen=args.armlength+50

	if not args.output.lower().endswith(".msdesc"): args.output+=".msdesc"
	fout=open(args.output,"w")

	try:
		mssdef=FormatFile(args.template)
	except Exception as e:
		logging.error(str(e))
		sys.exit(-1)

	fastafiles=args.FASTAFILES

	fout.write("# [Locus]\t[Pattern]\t[Left flanking seq]\t[Right Flank Seq]\t[MS]\n")
	for i in fastafiles:
		ff=FastaFile(i)
		for j in ff.getChromosomes():
			for start,end,repeatsize,chrn in mssdef[j]:
				ch=ff.getChunk(j,start-armlen,end-start+1+armlen*2)
				createBaits(ch,armlen,start,end,repeatsize,chrn,fout)

	fout.close()
	logging.info( " *** [ {0} ] *** WRITTEN!".format(args.output))
