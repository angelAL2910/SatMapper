import math

class BaitDesc:
	def __init__(self,baitdescstream):
		self.baitdescs={}
		for i in baitdescstream:
			if i.startswith("#"): continue
			i=i.split("\t")
			self.baitdescs[i[0]]=[i[1],i[2],i[3]]

	# Generates a simple bait
	def generate(self,baitid,repeats):
		pattern,left,right=self.baitdescs[baitid]
		return left+pattern*repeats+right

	# Generates a list of baits given limits of repeats
	def generatelist(self,minrep,maxrep,outstream):
		for bait,pars in self.baitdescs.items():
			pattern,left,right=pars
			min=int(math.ceil(float(minrep)/len(pattern)))
			max=int(math.floor(float(maxrep)/len(pattern)))+1
			repeatsize=len(pattern)
			armsize=len(left)
			for i in range(min,max):
				baitid="{0}:{1}:{2}:{3}:{4}:{5}".format(bait,i,repeatsize,i*repeatsize,armsize,armsize+repeatsize*i)
				outstream.write(">"+baitid+"\n")
				outstream.write(left+pattern*i+right+"\n")

	# Gets a bait chung given a read and the alignment position
	def chunk(self,key,read,readstart,reverse):
		lread=len(read)-1
		key=key.split(":")
		repeats=int(key[1])
		baitid=key[0]
		gen=self.generate(baitid,repeats)
		gen=gen[readstart:readstart+len(read)]
		cad=[]
		if not reverse:
			for i in range(len(gen)):
				if gen[i]!=read[i]:
					cad.append("{0}:{1}>{2}".format(i,gen[i],read[i]))
		else:
			for i in range(len(gen)-1,-1,-1):
				if gen[i]!=read[i]:
					cad.append("{0}:{1}>{2}".format(lread-i,gen[i],read[i]))

		return ",".join(cad)
