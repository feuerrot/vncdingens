#!/usr/bin/env python3
import struct
import socket
import os

logf = 'logfile'
host = ''
port = 5900

log = open('logfile', 'a')

fbupdate = True

SetPixelFormat = b'\x00'
SetEncoding = b'\x02'
FrameBufferUpdateRequest = b'\x03'
KeyEvent = b'\x04'
PointerEvent = b'\x05'
ClientCutText = b'\x06'

p_protoversion = b'RFB 003.003\n'
p_securityhandshake = b'\x00\x00\x00\x01'
p_serverinit = b'\x00\xFF\x00\xFF'
PIXFMT = b'\x20\x20\x01\x01\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00'
p_servername = b'\x00\x00\x00\x08feuerrot'
p_bell = b'\x02'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(True)
s.bind((host, port))
s.listen(1)

def read_spf(s):
	#print("read_sfp")
	s.recv(3) # Padding
	PIXFMT = s.recv(16)
	#print(PIXFMT)

def read_enc(s):
	#print("read_enc")
	s.recv(1) # Padding
	n = s.recv(2)
	(n,) = struct.unpack(">H", n)
	#print("Anzahl Encodings: {}".format(n))
	for i in range(n):
		s.recv(4)

def read_fbur(s):
	#print("read_fbur")
	inc = s.recv(1)
	xpos = s.recv(2)
	ypos = s.recv(2)
	xsize = s.recv(2)
	ysize = s.recv(2)
	#print("inc: {} xpos: {} ypos: {} xsize: {} ysize: {}".format(inc, xpos, ypos, xsize, ysize))
	fbupdate = True

def read_key(s):
	#print("read_key")
	down = s.recv(1)
	s.recv(2) # Padding
	key = s.recv(4)

def read_pointer(s):
	#print("read_pointer")
	button = s.recv(1)
	xpos = s.recv(2)
	ypos = s.recv(2)

def read_cct(s):
	#print("read_cct")
	s.recv(3) # Padding
	n = s.recv(4)
	(n,) = struct.unpack(">I", n)
	s.recv(n)

def readpacket(s):
	data = s.recv(1)
	if data == SetPixelFormat:
		read_spf(s)
	elif data == SetEncoding:
		read_enc(s)
	elif data == FrameBufferUpdateRequest:
		read_fbur(s)
	elif data == KeyEvent:
		read_key(s)
	elif data == PointerEvent:
		read_pointer(s)
	elif data == ClientCutText:
		read_cct(s)
	
def send_fbupdate(s):
	fbupdate = False
	data = bytearray()
	data += b'\x00'
	data += b'\x00' # Padding
	data += b'\x00\x01'

	data += b'\x00\x00\x00\x00' # Start: x=0 y=0
	data += b'\x00\xFF\x00\xFF' # Size: x=255 y=255
	data += b'\x00\x00\x00\x00' # Raw encoding

	data += os.urandom(255**2)
	s.send(data)

while True:
	conn, addr = s.accept()
	print("Accepted connection from {}".format(addr))
	log.write("Accepted connection from {}\n".format(addr))
	log.flush()

	try:
		conn.send(p_protoversion)
		data = conn.recv(1024)
		print(data)
		
		conn.send(p_securityhandshake)
		data = conn.recv(1)
		print(data)

		conn.send(p_serverinit + PIXFMT + p_servername)

		while True:
			readpacket(conn)
			if fbupdate:
				send_fbupdate(conn)

	except ConnectionResetError:
		conn.close()
		pass

	except Exception as e:
		print(e.__doc__)
		conn.close()
		pass
	conn.close()
s.close()
log.close()


