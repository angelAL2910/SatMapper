import sys
import pysam
import getopt
import logging
from lib.gmod import GMOD
from lib.BaitDesc import BaitDesc

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

class Dealer:
	def __init__(self,saminfo):
		self.saminfo=saminfo
		self.references=[]

	def next(self):
		i= self.saminfo.__iter__().next()
		return i,self.saminfo.references[i.tid]

	def __iter__(self):
		return self

if __name__=="__main__":
	optlist, args = getopt.getopt(sys.argv[1:],'')

	optlist=dict(optlist)

	if not args:
		logging.error("Insufficient parameters: {0} <ms.fa.msdesc>".format(sys.argv[0]))
		sys.exit(-1)

	bg=BaitDesc(open(sys.argv[1]))
	samfile = pysam.Samfile("-", "r" )
	
	deal=Dealer(samfile)
	dbconn=GMOD.getDBConn()
	
	for i,ref in deal:
		spref=ref.split(":")
		qname=i.qname.split("@")
		sample=qname[0]
		qname.pop(0)
		readname="@".join(qname)
		nrepeats=int(spref[1])
		lenrepeat=int(spref[2])
		lenms=int(spref[3])
		startms=int(spref[4])
		endms=int(spref[5])
		read=i.seq
		qua=i.qual
		readstart=i.pos
		reverse=i.is_reverse
		gen=bg.chunk(ref,read,readstart,reverse)
		lenread=len(read)

		if readstart>=startms and readstart+lenread<endms: continue

		if readstart<startms and readstart+lenread>endms:
			atype=1
			llen=startms-readstart
			rlen=readstart+lenread-endms
			mlen=int(spref[3])
		elif readstart<startms and readstart+lenread>startms and readstart+lenread<=endms:
			atype=0
			llen=startms-readstart
			rlen=0
			mlen=readstart+lenread-startms
		elif readstart>=startms and readstart<endms and readstart+lenread>endms:
			atype=2
			llen=0
			mlen=endms-(readstart)
			rlen=readstart+lenread-endms
		elif readstart+lenread<startms:
			continue
			atype=4
			llen=lenread
			mlen=rlen=0
		elif readstart>endms:
			continue
			atype=5
			rlen=lenread
			mlen=llen=0
		else:
			continue


		lmism=rmism=mmism=0
		if not gen: mismpos=[]
		else: mismpos=[int(i.split(":")[0]) for i in gen.split(",")]

		if reverse:
			mismpos=[lenread-1-i for i in mismpos]

		for i in mismpos:
			if i<llen: lmism+=1
			elif i<llen+mlen: mmism+=1
			else: rmism+=1

		dbconn.addRead(sample,readname,spref[0],nrepeats,lenrepeat,lenms,startms,endms,read,readstart,gen,qua,llen,mlen,rlen,atype,lmism,rmism,mmism,reverse,0)

	dbconn.commit()


