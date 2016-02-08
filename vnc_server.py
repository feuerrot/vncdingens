#!/usr/bin/env python3
import struct
import socket

logf = 'logfile'
host = ''
port = 5900

log = open('logfile', 'a')

PIXFMT = None

SetPixelFormat = b'\x00'
SetEncoding = b'\x02'
FrameBufferUpdateRequest = b'\x03'
KeyEvent = b'\x04'
PointerEvent = b'\x05'
ClientCutText = b'\x06'

p_protoversion = b'RFB 003.003\n'
p_securityhandshake = b'\x00\x00\x00\x01'
p_serverinit = b'\x00\xFF\x00\xFF\x20\x20\x01\x01\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08feuerrot'
p_bell = b'\x02'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(True)
s.bind((host, port))
s.listen(1)

def read_spf(s):
	print("read_sfp")
	s.recv(3) # Padding
	PIXFMT = s.recv(16)
	print(PIXFMT)

def read_enc(s):
	print("read_enc")
	s.recv(1) # Padding
	n = s.recv(2)
	(n,) = struct.unpack(">H", n)
	print("Anzahl Encodings: {}".format(n))
	for i in range(n):
		s.recv(4)

def read_fbur(s):
	print("read_fbur")
	inc = s.recv(1)
	xpos = s.recv(2)
	ypos = s.recv(2)
	xsize = s.recv(2)
	ysize = s.recv(2)

def read_key(s):
	print("read_key")
	down = s.recv(1)
	s.recv(2) # Padding
	key = s.recv(4)

def read_pointer(s):
	print("read_pointer")
	button = s.recv(1)
	xpos = s.recv(2)
	ypos = s.recv(2)

def read_cct(s):
	print("read_cct")
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

		conn.send(p_serverinit)

		while True:
			readpacket(conn)
	except Exception as e:
		print(e.__doc__)
		print(e.message)
		conn.close()
		pass
	conn.close()
s.close()
log.close()


