import gzip
import bz2
import sys
import tempfile
import logging
from optparse import OptionParser
import re

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
	def __init__(self,formatfile):
		j=0
		a=open(formatfile)
		self.chrid_to_n={}
		self.microsatellites={}
		for i in a:
			j+=1
			if not i.strip() or i.startswith("#"): continue
			i=i.strip().split("\t")
			try:
				chrn=int(i.pop(0))
				start=int(i.pop(0))
				end=int(i.pop(0))
				repeatsize=int(i.pop(0))
				fastaid="\t".join(i)
				self.chrid_to_n.setdefault(fastaid,chrn)
			except:
				raise Exception("Error in microsatellite description file (line {0}), invalid format.\nIt must be 6 tab separated fields.".format(j))

			if (end+1-start)%repeatsize:
				raise Exception("Error in microsatellite description file (line {0}).\nMicrosatellite length does not match with repeat length.".format(j))

			if self.chrid_to_n[fastaid]!=chrn:
				raise Exception("Error in microsatellite description file (line {0}).\nfastaID does not match with chromosome number.".format(j))

			self.microsatellites.setdefault(fastaid,[]).append((start,end,repeatsize,chrn))

	def __getitem__(self,item):
		if item in self.microsatellites:
			msslist=self.microsatellites[item]
			del self.microsatellites[item]
			return msslist
		return []

def patternDetect(cad,patlen):
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



	

def createBaits(chunk,armsize,start,end,repeatsize,chrn,output):
	left,right,ms=chunk[:armsize],chunk[-armsize:],chunk[armsize:-armsize]
	pattern=patternDetect(ms,repeatsize)

	if not re.match("^({0})+$".format(pattern),ms):
		output.write( "# Chr {3}, Pos {4} : ...{0} | {1} | {2}... NOT PURE!!!!\n".format(left[-20:],ms,right[:20],chrn,start))

	output.write("{0}_{1}_{2}\t{6}\t{3}\t{4}\t{5}\n".format(chrn,pattern,start,left,right,ms,pattern))



if __name__=="__main__":
	parser = OptionParser(usage="usage: %prog <-t mss_spec_template.txt -o template.out f1.fa f2.fa.gz ...>")
	parser.add_option("-t", "--template", dest="template", help="File containing the microsatellite spacification list.")
	parser.add_option("-o", "--output", dest="outfile", help="Specify file out either for template or the baits fasta. If it is not specified, stdout will be used.")
	parser.add_option("-l", "--armlength", dest="armlength", help="Specify flanking sequence sength for the baits [100 by default].")
	armlen=100

	(options, args) = parser.parse_args()

	if options.armlength:
		armlen=int(options.armlength)

	if not options.template: parser.error("You must specify a file containing a microsatellite template [-t]")
	if not args: parser.error("You must specify at least a fasta file.")
	
	fout=sys.stdout
	if options.outfile:
		if not options.outfile.lower().endswith(".msdesc"): options.outfile+=".msdesc"
		fout=open(options.outfile,"w")

	try:
		mssdef=FormatFile(options.template)
	except Exception as e:
		logging.error(str(e))
		sys.exit(-1)

	fastafiles=args

	fout.write("# [Locus]\t[Pattern]\t[Left flanking seq]\t[Right Flank Seq]\t[MS]\n")
	for i in fastafiles:
		ff=FastaFile(i)
		for j in ff.getChromosomes():
			for start,end,repeatsize,chrn in mssdef[j]:
				ch= ff.getChunk(j,start-armlen,end-start+1+armlen*2)
				createBaits(ch,armlen,start,end,repeatsize,chrn,fout)

	fout.close()
