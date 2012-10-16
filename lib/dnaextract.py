import gzip
import bz2
import sys
import tempfile
import logging
import getopt
import re

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

#### Input file format is:
#### genebankId MarshfieldID Start   End     FastA ID
#### 1sdfasdf   asdfasdfasdf 10000   10100   1 dna:chromosome chromosome:GRCh37:1:1:249250621:1


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
		self.microsatellites={}
		for i in a:
			j+=1
			if not i.strip() or i.startswith("#"): continue
			i=i.strip().split("\t")
			try:
				geneid=i.pop(0)
				marshid=i.pop(0)
				start=int(i.pop(0))
				end=int(i.pop(0))
				fastaid="\t".join(i)
			except:
				raise Exception("Error in microsatellite description file (line {0}), invalid format.\nIt must be 6 tab separated fields.".format(j))

			self.microsatellites.setdefault(fastaid,[]).append((start,end,geneid,marshid))

	def __getitem__(self,item):
		if item in self.microsatellites:
			msslist=self.microsatellites[item]
			del self.microsatellites[item]
			return msslist
		return []


if __name__=="__main__":

	optlist, args = getopt.getopt(sys.argv[1:], 'o:')

	optlist=dict(optlist)


	if len(args)<2:
		logging.error("Insufficient parameters: {0} <MS_definition.txt> <fasta1.fa> <fasta2.fa> ... <fastaN.fa>".format(sys.argv[0]))
		sys.exit(-1)

	try:
		mssdef=FormatFile(args[0])
	except Exception as e:
		logging.error(str(e))
		sys.exit(-1)

	fastafiles=args[1:]

	for i in fastafiles:
		ff=FastaFile(i)
		for j in ff.getChromosomes():
			for start,end,geneid,marshid in mssdef[j]:
				ch= ff.getChunk(j,start,end-start)
				print geneid+"\t"+marshid+"\t"+str(start)+"\t"+str(end)+"\t"+ch
