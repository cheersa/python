# -*- coding: UTF-8 -*-
from socket import *
import getpass
import threading
import sys
import os
import time

USER_NOT_EXSIT = 0
AUTH = 1
PASS_FAIL = 2
PASS_THREE_FAIL = 3
USER_DUP = 4

sock = socket()
is_close = False
last_recv = ""

def sendThreadFunc():
	global is_close
	while True:  
		try:  
			message = input(">")
			if is_close:
				break
			if message == 'logout':
				sock.send(message.encode())
				is_close = True
				break
			if message == 'y' or message == "Y":
				if "info" in last_recv and "receive" in last_recv and "file" in last_recv:
					tmp = last_recv.split(" ")
					tmp2 = last_recv.split("file_name:")
					message = "Y,"+tmp2[1]+","+tmp[5]
					sock.send(message.encode())
					file_name = tmp2[1]
				else:
					sys.stdout.write("\command error\n>")
					sys.stdout.flush()
			if "sendfile" in message:
				cmd = message.split(" ")
				
				if len(cmd) != 3:
					sys.stdout.write("\command error\n>")
					sys.stdout.flush()
					continue
				file_name = "client_send/"+cmd[2]
				#file send
				
				if os.path.exists(file_name):
					sock.send(message.encode())
					time.sleep(1);
					file = open(file_name, 'rb')
					while True:
						data = file.read(1024)
						if not data:
							break
						sock.send(data)
					file.close()
				else:
					print("file(%s) does not exist,please recheck."%(file_name))
			else:
				sock.send(message.encode())
		except ConnectionAbortedError:  
			print('Server closed this connection!')  
			break
		except ConnectionResetError:  
			print('Server is closed!')
			break
	print("bye")
	sock.close()
	  
def recvThreadFunc():
	global last_recv
	global is_close
	while True:  
		try:
			if is_close:
				break
			message = sock.recv(1024).decode()

			if "[info]transmit file_name:" in message:
				tmp = message.split("file_name:")
				file_name = tmp[1]
				dir = "client_recv/"
				
				if os.path.exists(dir+file_name):
					os.remove(dir+file_name)
				file = open(dir+file_name, 'wb')
				result = False
				while True:
					content = sock.recv(1024)
					file.write(content)
					length = len(content)
					if length<1024:
						result = True
						break
				file.flush() 
				file.close()
				sys.stdout.write("\bend transmit\n>")
				sys.stdout.flush()
				last_recv = ""
				file_name = ""
			else:
				if message:
					sys.stdout.write("\b"+message+"\n>")
					sys.stdout.flush()
					last_recv = message
				else:  
					pass
		except ConnectionAbortedError:  
			print('Server closed this connection!')  
		except ConnectionResetError:  
			print('Server is closed!')

if __name__ == '__main__':
	 
	
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.connect(('',8080))
	
	message = input("login:")
	sock.send(message.encode())
	while True:
		message = getpass.getpass("password:")
		sock.send(message.encode()) 
		data = sock.recv(1024).decode().split(",")
		auth = int(data[0])
		info = data[1]
		print (info)
		if auth == AUTH or auth == PASS_THREE_FAIL or auth == USER_NOT_EXSIT or auth == USER_DUP:
			break
		
		
	if auth == AUTH:
		th1 = threading.Thread(target=sendThreadFunc)
		th2 = threading.Thread(target=recvThreadFunc)
		threads = [th1, th2]
		for t in threads :  
			t.setDaemon(True)  
			t.start()  
		t.join()
				 
		sock.close()