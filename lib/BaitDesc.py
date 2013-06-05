#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

import math


class BaitDesc:
	def __init__(self,baitdescstream):
		self.baitdescs={}
		self.deleted=set()
		for i in baitdescstream:
			if i.startswith("#"): continue
			i=i.strip().split("\t")
			pattern,left,right=i[1],i[2],i[3]
			#left,right=i[1],i[2]
			#pattern=i[0].split("_")[1]
			while not len(pattern)%2 and pattern[:len(pattern)/2]==pattern[len(pattern)/2:]:
				pattern=pattern[:len(pattern)/2]
			self.baitdescs[i[0]]=[pattern,left,right]


	def minSeparation(self,space,mslen=100,avoid=[]):
		data={}
		for i in self.baitdescs:
			chr,pat,pos=i.split(".")[0].split("_")
			pos=int(pos)
			data.setdefault(chr,[]).append((pos,i))

		for i in data.values():
			i.sort()
			distances=[]
			for j in range(1,len(i)-1):
				distances.append((i[j][0]-i[j-1][0],i[j+1][0]-i[j][0]))

			while True:
				deleted=0
				for j in range(len(distances)):
					j-=deleted
					if i[j+1][1] in avoid: continue
					if distances[j][0]<space and distances[j][1]<space+mslen:
						deleted+=1
						self.deleted.add(i[j][1])
						del distances[j]
						del i[j+1]
				if not deleted:break
					
			while True:
				deleted=0
				for j in range(len(distances)):
					j-=deleted
					if i[j+1][1] in avoid: continue
					if distances[j][0]<space or distances[j][1]<space+mslen:
						deleted+=1
						self.deleted.add(i[j][1])
						del distances[j]
						del i[j+1]
				if not deleted:break


	def dump(self):
		uniq=set()
		for i,j in self.baitdescs.items():
			arms=j[1][-10:]+j[2][:10]
			if i not in self.deleted:
				if arms in uniq: continue
				uniq.add(arms)
				uniq.add(self.reverseComplement(arms))
				print "\t".join([i]+j)

	def reverseComplement(self,cad):
		dic={"A":"T","T":"A","G":"C","C":"G","N":"N","-":"-"}
		return "".join([dic[i] for i in cad][::-1])
						
			

	# Generates a simple bait
	def generate(self,baitid,repeats):
		pattern,left,right=self.baitdescs[baitid]
		if "." not in baitid:
			return left+pattern*repeats+right
		else:
			fraction=""
			fn=int(baitid.split(".")[1])
			for i in range(fn):
				fraction+=pattern[i%len(pattern)]

			return left+pattern*repeats+fraction+right
			



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


if __name__=='__main__':
	import sys
	a=BaitDesc(open(sys.argv[1]))
	b=BaitDesc(open(sys.argv[2]))
	b.minSeparation(110)
	a.minSeparation(110,100,set(b.baitdescs.keys()).difference(b.deleted))
	a.dump()
	

