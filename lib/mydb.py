import MySQLdb
from MySQLdb import cursors

class DbWrapper:
	def __init__(self):
		pass

	def createSample(self,samplename):
		pass

	def addRead(self,sample,readname,ref,nrepeats,lenrepeat,lenms,startms,endms,read,readstart,gen,qua,llen,mlen,rlen,atype,lmism,rmism,mmism,reverse,decim):
		pass

	def commit(self):
		pass

	def getSamples(self):
		pass

	def getFields(self,sample):
		pass

	def select(self,query):
		pass

	def executemany(self,query,data):
		pass


class DB_Mysql:
	def __init__(self,user,passwd,db,host="localhost",port=3307,sock=None):
		self.db=MySQLdb.connect(user=user,db=db,passwd=passwd,host=host,port=port,unix_socket=sock)
		self.cursor=self.db.cursor()

	def createSample(self,samplename):
		try:
			self.cursor.execute('''CREATE TABLE `{0}` ( `ROWID` int(11) unsigned NOT NULL AUTO_INCREMENT, `readname` char(100) NOT NULL DEFAULT '', `ref` char(25) NOT NULL DEFAULT '', `nrepeats` tinyint(1) unsigned NOT NULL, `lenrepeat` tinyint(1) unsigned NOT NULL, `lenms` smallint(2) unsigned NOT NULL, `startms` int(11) unsigned NOT NULL, `endms` int(11) unsigned NOT NULL, `read` varchar(1000) NOT NULL DEFAULT '', `readstart` int(11) unsigned NOT NULL, `gen` varchar(1000) NOT NULL DEFAULT '', `qua` varchar(1000) NOT NULL DEFAULT '', `llen` smallint(11) unsigned NOT NULL, `mlen` smallint(11) unsigned NOT NULL, `rlen` smallint(11) unsigned NOT NULL, `atype` tinyint(11) unsigned NOT NULL, `lmism` tinyint(11) unsigned NOT NULL, `rmism` tinyint(11) unsigned NOT NULL, `mmism` tinyint(11) unsigned NOT NULL, `reverse` tinyint(11) unsigned NOT NULL, `decim` tinyint(11) unsigned NOT NULL, `score` smallint(11) unsigned NOT NULL DEFAULT '0', `allele` float unsigned NOT NULL, PRIMARY KEY (`ROWID`), KEY `ref` (`ref`), KEY `nrepeats` (`nrepeats`), KEY `lenrepeat` (`lenrepeat`), KEY `lenms` (`lenms`),  KEY `allele` (`allele`))'''.format(samplename))
		except: pass

	def addRead(self,sample,readname,ref,nrepeats,lenrepeat,lenms,startms,endms,read,readstart,gen,qua,llen,mlen,rlen,atype,lmism,rmism,mmism,reverse,decim):
		readname=self.db.escape_string(readname)
		ref=self.db.escape_string(ref)
		read=self.db.escape_string(read)
		gen=self.db.escape_string(gen)
		qua=self.db.escape_string(qua)

		try:	
			self.cursor.execute('''insert into {0} (`readname`,`ref`,`nrepeats`,`lenrepeat`,`lenms`,`startms`,`endms`,`read`,`readstart`,`gen`,`qua`,`llen`,`mlen`,`rlen`,`atype`,`lmism`,`rmism`,`mmism`,`reverse`,`decim`,`allele`) VALUES ('{1}','{2}',{3},{4},{5},{6},{7},'{8}',{9},'{10}','{11}',{12},{13},{14},{15},{16},{17},{18},{19},{20},{3})'''.format(sample,readname,ref,nrepeats,lenrepeat,lenms,startms,endms,read,readstart,gen,qua,llen,mlen,rlen,atype,lmism,rmism,mmism,reverse,decim))
		except Exception as e:
			if e.args[0]==1146:
				self.createSample(sample)
				self.cursor.execute('''insert into {0} (`readname`,`ref`,`nrepeats`,`lenrepeat`,`lenms`,`startms`,`endms`,`read`,`readstart`,`gen`,`qua`,`llen`,`mlen`,`rlen`,`atype`,`lmism`,`rmism`,`mmism`,`reverse`,`decim`,`allele`) VALUES ('{1}','{2}',{3},{4},{5},{6},{7},'{8}',{9},'{10}','{11}',{12},{13},{14},{15},{16},{17},{18},{19},{20},{3})'''.format(sample,readname,ref,nrepeats,lenrepeat,lenms,startms,endms,read,readstart,gen,qua,llen,mlen,rlen,atype,lmism,rmism,mmism,reverse,decim))

	def commit(self):
		self.db.commit()

	def getSamples(self):
		self.cursor.execute("show tables")
		return [i[0] for i in self.cursor]

	def getFields(self,sample):
		self.cursor.execute("show columns from {0}".format(sample))
		res=[i[0] for i in self.cursor][1:]
		return res
	
	def select(self,query):
		c=self.db.cursor(cursors.SSCursor)
		c.execute(query)
		return c

	def executemany(self,query,data):
		self.cursor.executemany(query,data)
