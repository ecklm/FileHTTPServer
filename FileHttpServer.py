#! /usr/bin/python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler
import mimetypes
import sys
from utility_classes import *

file_to_send_full_path = None # Full path of the file to be served
file_name = None # Name of the file to be served
send_block_size = None # Unit of reading from the stream (bytes)
file_type = FileType.undecided # Type of the file to be served

class FileRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-Type', mimetypes.guess_type(file_to_send_full_path)[0])
		self.send_header('Connection', 'close')
		self.send_header('Content-Disposition', 'attachment;'
	                    'filename=%s' % file_name.encode().decode('latin-1')) # This function wants to decode it from latin-1. Not fully appropriate solution.

		if file_type==FileType.zipstream:
			sendThread=ZipStream(file_to_send_full_path)
			sendThread.start()
			file_stream=sendThread.getPipein()
		elif file_type==FileType.realfile:
			file_stream = open(file_to_send_full_path, 'rb')
			file_size = os.path.getsize(file_to_send_full_path)
			self.send_header("Content-Length", file_size)
		else:
			raise ("Gosh! Neither a file nor a directory!?")
		self.end_headers()

		x=file_stream.read(send_block_size)
		while x!=b'':
			self.wfile.write(x)
			x=file_stream.read(send_block_size)
		file_stream.close()

if __name__ == '__main__':
	try:
		file_to_send_full_path = get_rid_of_last_path_sep(sys.argv[1])
	except IndexError:
		sys.stderr.write("You didn't enter any file path.\n")
		sys.exit(1)


	# Initializing the serving propertioes for the selected file
	try:
		if os.path.isdir(file_to_send_full_path): # Returns false even if the file doesn't exist
			file_name=os.path.basename(file_to_send_full_path + ".zip")
			send_block_size = 4096 # Experimental value
			file_type = FileType.zipstream
		else:
			file_stream = open(file_to_send_full_path, 'rb') # This throws an exception if the file doesn't exist
			file_name = os.path.basename(file_to_send_full_path)
			send_block_size = 4096000 # Experimental value
			file_type = FileType.realfile
	except FileNotFoundError:
		sys.stderr.write("There is no such file or directory: '" + file_to_send_full_path + "'\n")
		sys.exit(1)
	################################################################

	BIND_ADDRESS_V6 = "::"
	server_port = 8080

	server = ServerThread()
	server.set_server(ServerV6((BIND_ADDRESS_V6, server_port), FileRequestHandler))
	print ("Starting server on [%s]:%d" % (BIND_ADDRESS_V6, server_port))
	server.start()

	exit = False
	while (exit is False) or server.isAlive():
		try:
			command = input("Type 'exit' to stop the server.\n")
		except:
			command = "exit"
			sys.stderr.write("Interrupt/error happened. Exit command set.\n")
		if command == "exit":
			server.stop()
			exit = True
