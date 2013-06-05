#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

import ConfigParser
from lib.patterns import *

class Config(Singleton):
	def __init__(self,cfgFile):
		self.configs=MultiDic()
		self.configFile=cfgFile
		self.readFile()

	def readFile(self):
		cfg=ConfigParser.ConfigParser()
		cfg.read(self.configFile)
		self.configs=MultiDic()
		for i in cfg.sections():
			for j in cfg.items(i):
				self.configs[i][j[0]]=j[1].strip()

	def writeFile(self):
		cfg=ConfigParser.ConfigParser()
		data=self.getSource()

		for i,j in data:
			if not cfg.has_section(i.split(":")[0]):
				cfg.add_section(i.split(":")[0])
			cfg.set(i.split(":")[0],":".join(i.split(":")[1:]),j)

		f=open(self.configFile,"w")
		cfg.write(f)
		f.close()


	def readSource(self,source):
		self.configs=MultiDic()
		for i,j in source:
			i=i.split(":")
			item=self.configs
			for k in range(len(i)-1):
				item=item[i[k]]
			item[i[-1]]=j

	def getSource(self):
		data=[]
		for i in self.configs:
			data+=self.getSource2(self.configs,i)
		return data

	def getSource2(self,dic,cur):
		data=[]
		if isinstance(dic[cur.split(":")[-1]],MultiDic):
			for i in dic[cur.split(":")[-1]]:
				data+=self.getSource2(dic[cur.split(":")[-1]],cur+":"+i)
		else:
			return [[cur,dic[cur.split(":")[-1]]]]
		return data

	def __getitem__(self,key):
		return self.configs[key]

	def __setitem__(self,key,value):
		self.configs[key]=value


class MultiDic:
	def __init__(self):
		self.values={}
		pass

	def __getitem__(self,key):
		return self.values.setdefault(key,MultiDic())

	def __setitem__(self,key,value):
		self.values[key]=str(value)

	def __iter__(self):
		return self.values.__iter__()

	def __str__(self):
		return str(self.values)

######################################################################################


