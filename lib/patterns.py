#!/usr/bin/python
# SatMapper - 2012-2013 Carlos del Ojo and John Cole.
# This code is part of the SATMAPPER software and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

class Singleton(object):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls)
		return cls._instance
