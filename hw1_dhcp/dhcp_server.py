from socket import *
import struct
from uuid import getnode
from random import randint
import binascii
"""
DHCP Server

calss:
DHCPDiscover(unpack packet)
DHCPOffer(build packet)
DHCPRequest(unpack packet)
DHCPACK(build packet)
"""
DISCOVER = 1
OFFER = 2
REQUEST = 3
ACK = 5

def generateXid():
	xid=b''
	for i in range(4):
		t = randint(0, 255)
		xid += struct.pack('!B', t)
	return xid
	
def generateMac():
	mac = str(getnode())
	print(mac)
	print (len(mac))
	mac = mac[0:12]
	macBytes = b''
	macBytes = binascii.unhexlify(mac)
	return macBytes
	
def transMac(data):
	mac=''
	for i in range(0,len(data)):
		tmp = str(hex(data[i]))
		mac += tmp[2:]
		mac += ':'
	mac = mac[:-1]
	return mac
	
def transXid(data):
	xid = ''
	for i in range(0,len(data)):
		tmp = str(hex(data[i]))
		xid += tmp[2:]
	xid = '0x'+xid
	return xid
	
class DHCPDiscover:
	def __init__(self,data):
		self.xid = b''
		self.mac = b''
		self.unpack(data)
		
	def unpack(self,data):
		self.xid = data[4:8]
		self.mac = data[28:34]
		print("[Server] receives DHCP Discover packet------------------")
		print("TransationID:"+transXid(self.xid))
		print("MAC:"+transMac(self.mac))
		
class DHCPOffer:
	def __init__(self,xid,mac):
		self.xid = xid
		self.mac = mac
		self.serverIP = '192.168.1.1'
		self.offerIP = '192.168.1.100'
		self.subnetMask = '255.255.255.0'
		self.leaseTime = 86400
		self.dhcpServer = '192.168.1.1'
		self.router = '192.168.1.1'
		self.dns = ['9.7.10.15','9.7.10.16','9.7.10.18']
		self.print_info()
		
	def print_info(self):
		print("[Server] send DHCP Offer packet-------------------------")
		print("TransationID:"+transXid(self.xid))
		print("MAC:"+transMac(self.mac))
		print("DhcpServer:"+self.dhcpServer)
		print("OfferIP:"+self.offerIP)
	
	def buildPacket(self):
		packet = b''
		packet  = b'\x02'   #Message type: Boot Reply (2)
		packet += b'\x01'   #Hardware type: Ethernet
		packet += b'\x06'   #Hardware address length: 6
		packet += b'\x00'   #Hops: 0 
	
		packet += self.xid       #Transaction ID
		packet += b'\x00\x00'    #Seconds elapsed: 0
		packet += b'\x00\x00'   #Bootp flags: 0x0000(unicast) + reserved flags
		packet += inet_aton('0.0.0.0')    #Client IP address: 0.0.0.0
		packet += inet_aton(self.offerIP)    #Your (client) IP address: 0.0.0.0
		packet += inet_aton(self.serverIP)    #Next server IP address
		packet += inet_aton('0.0.0.0')    #Relay agent IP address
		#CHADDR(16byte)
		packet += self.mac    #Client MAC address
		packet += b'\x00' *10    #Client hardware address padding
		packet += b'\x00' * 192
	
		packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
		
		packet += b'\x35\x01\x02'   #Option: (t=53,len=1,value=2) DHCP Message,DHCP Offer
		packet += b'\x01\x04' #subnet mask option=1,len=1
		packet += inet_aton(self.subnetMask) #subnet mask content
		packet += b'\x03\x04' #router option=3,len=4
		packet += inet_aton(self.router) #router
		packet += b'\x33\x04' #leaseTime option=51,len=4
		packet += (self.leaseTime).to_bytes(4,byteorder="big") #leaseTime 
		packet += b'\x36\x04' #server ip option=54,len=4
		packet += inet_aton(self.dhcpServer)
	
		#DNS
		for i in range(0,len(self.dns)):
			packet += b'\x06\x04' #dns option=6,len=4
			packet += inet_aton(self.dns[i])
			
		#End 
		packet += b'\xff'
		return packet

class DHCPRequest:
	def __init__(self,xid,data,serverIP):
		self.isRecv = 1
		self.xid = xid
		self.serverIP = serverIP
		self.unpack(data)

		
	def unpack(self,data):
		serverIP = '.'.join(map(lambda x:str(x), data[20:24]))
		type = int(data[242])
		
		if self.xid != data[4:8] or self.serverIP != serverIP or type != REQUEST:
			self.isRecv = 0
			print("[Server] receives other DHCP Request packet")
			return 

		print("[Server] receives DHCP Request packet-------------------")
		print("TransationID:"+transXid(self.xid))
		print("MAC:"+transMac(data[28:34]))
		print("Server IP:"+self.serverIP)
		print("OfferIP:"+'.'.join(map(lambda x:str(x), data[245:249])))
	
class DHCPACK:
	def __init__(self,xid,mac,offerIP,serverIP,subnetMask,router,leaseTime,dhcpServer,dns):
		self.xid = xid
		self.mac = mac
		self.serverIP = serverIP
		self.offerIP = offerIP
		self.subnetMask = subnetMask
		self.leaseTime = leaseTime
		self.router = router
		self.dhcpServer=dhcpServer
		self.dns = dns
		self.print_info()
		
	def print_info(self):
		print("[Server] send DHCP ACK packet---------------------------")
		print("TransationID:"+transXid(self.xid))
		print("MAC:"+transMac(self.mac))
		print("DhcpServer:"+self.dhcpServer)
		print("OfferIP:"+self.offerIP)
		
	def buildPacket(self):
		packet = b''
		packet  = b'\x02'   #Message type: Boot Reply(2)
		packet += b'\x01'   #Hardware type: Ethernet
		packet += b'\x06'   #Hardware address length: 6
		packet += b'\x00'   #Hops: 0 
	
		packet += self.xid       #Transaction ID
		packet += b'\x00\x00'    #Seconds elapsed: 0
		packet += b'\x00\x00'   #Bootp flags: 0x0000(unicast) + reserved flags
		packet += inet_aton('0.0.0.0')    #Client IP address: 0.0.0.0
		packet += inet_aton(self.offerIP)    #Your (client) IP address: 0.0.0.0
		packet += inet_aton(self.serverIP)    #Next server IP address
		packet += inet_aton('0.0.0.0')    #Relay agent IP address
		#CHADDR(16byte)
		packet += self.mac    #Client MAC address
		packet += b'\x00' *10    #Client hardware address padding
		packet += b'\x00' * 192
	
		packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
		
		packet += b'\x35\x01\x05'   #Option: (t=53,len=1,value=5) DHCP Message,DHCP ACK
		packet += b'\x01\x04' #Option:(t=1,len=4) subnet Mask 
		packet += inet_aton(self.subnetMask) #subnet Mask
		packet += b'\x03\x04' #Option:(t=3,len=4) router
		packet += inet_aton(self.router) #router
		packet += b'\x33\x04' #Option(t=51,len=4) leaseTime 
		packet += (self.leaseTime).to_bytes(4,byteorder="big") #leaseTime 
		packet += b'\x36\x04' #Option(t=54,len=4) DHCP Server
		packet += inet_aton(self.dhcpServer)#DHCP server
	
		#DNS
		for i in range(0,len(self.dns)):
			packet += b'\x06\x04' #Option(t=6,len=4) DNS
			packet += inet_aton(self.dns[i])
			
		#End 
		packet += b'\xff'
		return packet	

if __name__ == '__main__':

	dhcps = socket(AF_INET, SOCK_DGRAM)
	dhcps.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) 
	dhcps.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

	try:
		dhcps.bind(('', 67))    
	except Exception as e:
		print(e)
		dhcps.close()
		exit()
	dhcps.settimeout(20)
	
	try:
		while True:
			data = dhcps.recv(1024)
			discoverPkt = DHCPDiscover(data)

			offerPkt = DHCPOffer(discoverPkt.xid,discoverPkt.mac)
			dhcps.sendto(offerPkt.buildPacket(), ('<broadcast>', 68))

			while True:
				data = dhcps.recv(1024)
				requestPkt = DHCPRequest(discoverPkt.xid,data,offerPkt.serverIP)
				if requestPkt.isRecv == 1:
					break
					
			ackPacket = DHCPACK(discoverPkt.xid,discoverPkt.mac,offerPkt.offerIP,offerPkt.serverIP,offerPkt.subnetMask,offerPkt.router,offerPkt.leaseTime,offerPkt.dhcpServer,offerPkt.dns)
			dhcps.sendto(ackPacket.buildPacket(), ('<broadcast>', 68))

	except timeout as e:
		print(e)
	except KeyboardInterrupt as e:
		print(e)
	dhcps.close()
