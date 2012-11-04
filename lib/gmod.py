from lib.patterns import Singleton 
from lib.config import Config
from lib.mydb import DB_Mysql

class GlobalModule(Singleton):
	def __init__(self):
		self.config=Config("satmapper.cfg")


	def getDBConn(self):	
		if self.config["db"]["dbms"]=="mysql":
			return DB_Mysql(self.config["db"]["mysql-user"],self.config["db"]["mysql-passwd"],self.config["db"]["mysql-db"],self.config["db"]["mysql-host"],int(self.config["db"]["mysql-port"]),self.config["db"]["mysql-socket"])

GMOD=GlobalModule()
