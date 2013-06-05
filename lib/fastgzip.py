#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

import zlib
from StringIO import StringIO

class FastGzip:
	'''Module that implements a ultrafast gzip'''
	MAXSIZE=1024*16
	def __init__(self,path1=None,fileobj=None):
		assert not path1 or not fileobj
		self.dec = zlib.decompressobj(16+zlib.MAX_WBITS)
		if fileobj: self.fil1=fileobj
		else: self.fil1=open(path1,'rb')
		self.buff1=StringIO(self.dec.decompress(self.fil1.read(FastGzip.MAXSIZE)))


	def __iter__(self):
		line=""
		while True:
			for line in self.buff1:
				if line[-1]!="\n":
					break
				yield line

			if line and line[-1]=="\n": line=""
			infodec=self.fil1.read(FastGzip.MAXSIZE)
			info=line+self.dec.decompress(infodec)
			self.buff1=StringIO(info)
			if not infodec: break

		if line:
			yield line

	def seek(self,*args):
		self.dec = zlib.decompressobj(16+zlib.MAX_WBITS)
		self.fil1.seek(*args)
		self.buff1=StringIO()

	def close(self):
		self.fil1.close()

if __name__=="__main__":
	import sys
	a=FastGzip(sys.argv[1])
	for i in a:
		sys.stdout.write(i)

