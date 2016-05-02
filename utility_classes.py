import socket
import threading
from socketserver import ThreadingMixIn
import zipfile
import os
import io
from http.server import HTTPServer
from enum import Enum

def get_rid_of_last_path_sep(path):
	if path[-1] == os.path.sep:
		return path[:-1]
	else:
		return  path

class FileType(Enum):
	undecided = 0
	realfile = 1
	zipstream = 2

class ZipStream(threading.Thread):
	def __init__(self, dirToZip, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
		super(ZipStream, self).__init__(group, target, name,
		                                args, kwargs, daemon=daemon)
		self.__dirToZip=dirToZip
		(self.__readpipefd, self.__writepipefd) =os.pipe()

	def run(self):
		pipeout=io.FileIO(self.__writepipefd, "wb")
		z=zipfile.ZipFile(pipeout,"w", zipfile.ZIP_DEFLATED)
		for x in os.walk(self.__dirToZip):
			for y in x[2]:
				z.write(x[0]+"/"+y)
		z.close()
		#os.close(self.__pipefd[1])

	def getPipein(self):
		return io.FileIO(self.__readpipefd,"rb")

class ServerThread(threading.Thread):
	__server = None

	def set_server(self, server):
		"""
		:type server: HTTPServer
		"""
		self.__server = server

	def stop(self): #TODO meg kéne csinálni, hogy a futó zipper thread-eket is állítsa le
		if (self.__server != None) and (self.isAlive() == True):
			self.__server.shutdown()
			print("Server stopped serving on %s on port %s." %
			              (self.__server.server_address[0], self.__server.server_address[1])
			        )
		else:
			return

	def run(self):
		if self.__server != None:
			print("Server started listening on %s on port %s." %
			              (self.__server.server_address[0], self.__server.server_address[1])
			        )
			self.__server.serve_forever()
		else:
			return

class ServerV6(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
	address_family = socket.AF_INET6
