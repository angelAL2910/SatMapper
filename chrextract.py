import gzip
import bz2
import sys
import tempfile
import logging
import getopt
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
				armlen=int(i.pop(0))
				repeatsize=int(i.pop(0))
				minrep=int(i.pop(0))
				maxrep=int(i.pop(0))
				fastaid="\t".join(i)
				self.chrid_to_n.setdefault(fastaid,chrn)
			except:
				raise Exception("Error in microsatellite description file (line {0}), invalid format.\nIt must be 6 tab separated fields.".format(j))

			if (end+1-start)%repeatsize:
				raise Exception("Error in microsatellite description file (line {0}).\nMicrosatellite length does not match with repeat length.".format(j))

			if self.chrid_to_n[fastaid]!=chrn:
				raise Exception("Error in microsatellite description file (line {0}).\nfastaID does not match with chromosome number.".format(j))

			self.microsatellites.setdefault(fastaid,[]).append((start,end,armlen,repeatsize,minrep,maxrep,chrn))

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



	

def createBaits(chunk,armsize,start,end,repeatsize,minrep,maxrep,chrn,output):
	left,right,ms=chunk[:armsize],chunk[-armsize:],chunk[armsize:-armsize]
	pattern=patternDetect(ms,repeatsize)

	if not re.match("^({0})+$".format(pattern),ms):
		logging.warn( "Chr {3}, Pos {4} : ...{0} | {1} | {2}... NOT PURE!!!!".format(left[-20:],ms,right[:20],chrn,start))
	else:
		logging.debug( "Chr {3}, Pos {4} : ...{0} | {1} | {2}...".format(left[-20:],ms,right[:20],chrn,start))


	for i in range(minrep,maxrep+1):
		baitid="{0}_{1}_{2}:{3}:{4}:{5}:{6}:{7}".format(chrn,pattern,start,i,repeatsize,i*repeatsize,armsize,armsize+repeatsize*i)
		output.write(">{0}\n{1}\n".format(baitid,left+pattern*i+right))



if __name__=="__main__":

	optlist, args = getopt.getopt(sys.argv[1:], 'o:')

	optlist=dict(optlist)


	if "-o" in optlist and len(args)>1:
		output=open(optlist["-o"],"w")
	else:
		logging.error("Insufficient parameters: {0} -o outfile <MS_definition.txt> <fasta1.fa> <fasta2.fa> ... <fastaN.fa>".format(sys.argv[0]))
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
			for start,end,armsize,repeatsize,minrep,maxrep,chrn in mssdef[j]:
				ch= ff.getChunk(j,start-armsize,end-start+1+armsize*2)
				createBaits(ch,armsize,start,end,repeatsize,minrep,maxrep,chrn,output)

				#print "...{0} | {1} | {2}...".format(left[-20:],ms,right[:20])
