# -*- coding: UTF-8 -*-
from socket import *
import threading
import os
import time
USER_NOT_EXSIT = 0
AUTH = 1
PASS_FAIL = 2
PASS_THREE_FAIL = 3
PASS_REINPUT = 3;
USER_DUP = 4;

WARN_MSG={USER_NOT_EXSIT:'User is not exist',AUTH:'Login successfully',PASS_FAIL:'Access defined(password error)',PASS_THREE_FAIL:'Three failed password',USER_DUP:'User already login'}
	
class User:
	def __init__(self):
		self.user_list = {'amy':{'password':'aaa','status':'offline'},'john':{'password':'aaa','status':'offline'},'cheersa':{'password':'aaa','status':'offline'},'jane':{'password':'aaa','status':'offline'},'chen':{'password':'aaa','status':'offline'}}
		self.friend_list = {'amy':[],'john':[],'cheersa':[],'jane':[],'chen':[]}
		self.connection = {}
		self.leavedmsg = {}
		self.files={}
		#{send,recv=is_recv}
	def add_conn(self,name,conn):
		if name in self.connection:
			self.remove_conn(name)
			return
		self.connection[name]=conn
		
	def remove_conn(self,name):
		if name in self.connection:
			del self.connection[name]
	def check_user(self,name):
		if name in self.user_list:
			return True
		return False
	def check_login(self,name,password):
		if not name in self.user_list:
			auth = USER_NOT_EXSIT
		elif self.user_list[name]['password'] != password:
			auth = PASS_FAIL
		elif name in self.connection:
			auth = USER_DUP
		else:
			auth = AUTH
			self.user_list[name]['status']='online'
			
		return auth
		
	def logout(self,name):
		if name in self.user_list:
			self.user_list[name]['status']='offline'
		if name in self.connection:
			del self.connection[name]

	def add_friend(self,name,friend_name):
		if not friend_name in self.user_list:
			msg = "friend: %s is not in user list" %(friend_name)
		elif not friend_name in self.friend_list[name]:
			self.friend_list[name].append(friend_name)
			msg = "%s added into the friend list" %(friend_name)
		else:
			msg = "friend: %s exists in friend list" %(friend_name)
		return msg
		
	def remove_friend(self,name,friend_name):
		if not friend_name in self.user_list:
			msg = "friend: %s is not in user list" %(name)
		elif friend_name in self.friend_list[name]:
			self.friend_list[name].remove(friend_name)
			msg = "%s removed from the friend list" %(friend_name)
		else:
			msg = "friend: %s is not in friend list" %(friend_name)
		return msg	
		
	def get_friend_list(self,name):
		str = ""
		for friend in self.friend_list[name]:
			str = str+friend+" "+self.user_list[friend]['status']+"\n"
		if not str:
			str = "friend list is empty.\n"
		return str[:-1]
	def get_conn(self,name):
		if name in self.connection:
			return self.connection[name]
		return False
	
	def send_msg(self,name,name2,msg):
		#離線留言
		if not name2 in self.user_list:
			msg = "%s is not in user list" %(name2)
			return (False,msg)
		if not name2 in self.connection:
			msg = "Message from %s:%s" %(name,msg)
			if not name2 in self.leavedmsg:
				self.leavedmsg[name2] = '\n'+msg
			else:
				self.leavedmsg[name2] = self.leavedmsg[name2]+"\n"+msg
			msg = "%s is offline,and leave message!" %(name2)
			return (False,msg)
		else:
			msg = name + ":" + msg
			return(self.connection[name2],msg)
		
	def get_msg(self,name):
		msg=""
		if name in self.leavedmsg:
			msg = self.leavedmsg[name]
			del self.leavedmsg[name]
		if not msg:
			return False
		return msg
	
	def del_file_record(self,account,name,file_name):
		del self.files[account][name][file_name]
	
	def set_file_record(self,account,name,file_name,res=None):
		if res == "Y":
			res = 1
		elif res == "N":
			res =0
		else:
			res = -1
		if not account in self.files:
			self.files[account]={}
		if not name in self.files[account]:
			self.files[account][name]={}
		self.files[account][name][file_name]=res
	
		
def parse_command(str,account,user):
	cmd = str.split(" ")
	standard_cmd=["friend","send","sendfile"]
	try:
		if not cmd[0] in standard_cmd:
			return "command error"
		if cmd[0]=="friend":
			if cmd[1]=="list":
				return user.get_friend_list(account)
			elif cmd[1]=="add" and cmd[2]:
				return user.add_friend(account,cmd[2])
			elif cmd[1]=="rm" and cmd[2]:
				return user.remove_friend(account,cmd[2])
		elif cmd[0] == "send" and cmd[1] and cmd[2]:
			msg = cmd[2]
			for index in range(3,len(cmd)):
				if index>2:
					msg = msg+" "+cmd[index]
			return user.send_msg(account,cmd[1],msg)
		elif cmd[0] == "sendfile" and cmd[1] and cmd[2]:
		
			if user.check_user(cmd[1]) and account!=cmd[1]:
				user.set_file_record(account,cmd[1],cmd[2])
				return cmd
			else:
				return False
	except IndexError as e:
		return "command error"


def subThreadIn(conn,user): 
	
	account = conn.recv(1024).decode()

	num = 1
	while True :
		try:
			password = conn.recv(1024).decode()
			#檢查帳號密碼
			auth = user.check_login(account,password)
			#超過三次密碼輸入失敗
			if num >= 3:
				auth = PASS_THREE_FAIL
			else:
				num = num + 1			
			#結果送給client
			message = str(auth)+','+WARN_MSG[auth]
			conn.send(message.encode())
			if auth == PASS_THREE_FAIL or auth == USER_NOT_EXSIT or auth == AUTH or auth == USER_DUP:
				break
		except BrokenPipeError as e:
			print(e)
			break

	if auth == AUTH:
		user.add_conn(account,conn)
		msg = user.get_msg(account)
		if msg:
			conn.send(msg.encode())
		for user2 in user.friend_list:
			if account in user.friend_list[user2]:
				print(user2)
				conns = user.get_conn(user2)
				msg = "%s is online" %(account)
				conns.send(msg.encode())
		
		
		while True:
			
			try:
				data = conn.recv(1024).decode()
				if "Y," in data or "N," in data:
					tmp = data.split(",")
					user.set_file_record(tmp[2],account,tmp[1],tmp[0])
					#print(user.files)
				elif data == "logout":
					for user2 in user.friend_list:
						if user2 == account:
							continue
						if account in user.friend_list[user2]:
							conns = user.get_conn(user2)
							msg = "%s is offline" %(account)
							conns.send(msg.encode())
					break
				else:
					msg = parse_command(data,account,user)
				if not msg :
					continue
				elif msg == "command error":
					conn.send(msg.encode())
					continue
				if 'sendfile' in data and msg:
					dir = "server_recv/"
					recv_name = msg[1]
					file_name = msg[2]
					file_all = dir+msg[2]
					if os.path.exists(dir+file_name):
						os.remove(dir+file_name)
					file = open(dir+file_name, 'wb')
					result = False
					while True: 
						content = conn.recv(1024)
						file.write(content)
						#print("recv file:%s",content)
						if len(content)<1024:
							result = True
							break
					file.flush() 
					file.close()
					msg = 'file store in server'
					
					conn.send(msg.encode())
					
					conns = user.get_conn(recv_name)
					if result and conns:
						msg = '[info]Did you receive file from %s ? file_name:%s' %(account,file_name)
						conns.send(msg.encode())
						during= 15
						while during>0:
							res=user.files[account][recv_name][file_name]
							if res==0 or res==1:
								break
							during=during-1
							print("waiting:%d" %(during))
							time.sleep(1)
							
						if res == 1:
							msg = '[info]transmit file_name:%s' %(file_name)
							conns.send(msg.encode())
							time.sleep(2)
							file2= open(dir+file_name, 'rb')
							while True:
								content = file2.read(1024)
								if not content:
									break
								conns.send(content)
							file2.close()
							print ("[finish]send to %s,file:%s" %(recv_name,file_name))
							continue
						elif res == 0 :
							msg = 'Receive defined'
							conn.send(msg.encode())
						else:
							continue
						user.del_file_record(account,recv_name,file_name)
				elif 'send' in data :
					if msg[0]:
						conns = msg[0]
						conns.send(msg[1].encode())
					else:
						print ("message:" + msg[1])
						conn.send(msg[1].encode())
				else:
					print (msg)
					conn.send(msg.encode())
					
			except (OSError, ConnectionResetError):
				break
	user.remove_conn(account)
	user.logout(account)
	
	conn.close()
	
if __name__ == '__main__':
	user = User()
	sock = socket()
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.bind(('',8080))
	sock.listen(5)
	mythread = {}
	count = 1
	while True:  
		connection, addr = sock.accept()  
		print('Accept a new connection', connection.getsockname(), connection.fileno())  
		
		#为当前连接开辟一个新的线程 
		print(connection.fileno())
		mythread[count] = threading.Thread(target=subThreadIn, args=(connection, user))  
		mythread[count].setDaemon(True)  
		mythread[count].start()
		count = count + 1;
	sock.close()