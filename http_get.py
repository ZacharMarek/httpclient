#!/usr/bin/env python3
import re
import socket
import sys
import ssl

ht=['http','https']
hdr=""
obsah=""

def nacit(vstup_url):
	hdr=""
	data=""
	d=vstup_url.split(": ")
	if len(d)==2:
		hdr=d[0].lower()
		data=d[1].lower()
	return (hdr,data)

def nac_url(URL):

	dat=re.match('[a-z]*',URL)
	typ=dat[0]
	URL=URL.replace(typ+"://","")
	dat=re.match('([\w\-\.]+)',URL)
	hostname=dat[0]
	path=URL.replace(hostname,"")
	if path=="":
	   	path="/"
	return (typ,hostname,path)


URL=str(sys.argv[1])
typ,hostname,path=nac_url(URL)

if (typ in ht):
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	
	if typ=="http":
		s.connect((hostname,80))
	else:
		s.connect((hostname,443))
		s=ssl.wrap_socket(s)
		
	while True:
		f=s.makefile("rwb")
		f.write(f'GET {path} HTTP/1.1\r\n'.encode("ASCII"))
		f.write(f'Host: {hostname}\r\n'.encode("ASCII"))
		f.write(f'Accept-charset: UTF-8\r\n\r\n'.encode("ASCII"))
		f.write('\r\n'.encode("ASCII"))
		f.flush()
		
		l=f.readline().decode("ASCII")
		d=l.split(" ")
		stat_cislo=d[1]
		stat_txt=d[0]
		
		
		while l != "":
			hdr,data=nacit(l)
			headre={}
			headre[hdr]=data
			l=f.readline().decode("ASCII").strip()
			
			if stat_cislo=="200":
				break
			
			elif stat_cislo==("301"or"302"or"303"or"307"or"308"):
			
				typ,hostname,path=nac_url(headre["location"])
				f.close()
				s.close()
		
			else:
				sys.stderr.write(stat_cislo + stat_txt)
				f.close()
				s.close()
				sys.exit(1)
				break
			
if stat_cislo=="200":
	for i in headre:
		if i=="content-length":
			dlzka=int(headre["content-length"])
			data=f.read(dlzka).decode("ASCII")
			sys.stdout.buffer.write(obsah)
			break
		elif i=="transfer-encoding":
			while True:
				dlzka=f.readline().decode("ASCII")
				d=int(dlzka,16)
				data=f.read(d)
				sys.stdout.buffer.write(data)
			if not data:
				break
	f.readline()	
	f.flush()
	f.close()
	s.close()
	sys.exit(0)
else:
	sys.exit(1)
