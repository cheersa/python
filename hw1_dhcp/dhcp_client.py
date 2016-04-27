from socket import *
import struct
from uuid import getnode
from random import randint
import binascii

"""
DHCP Client

calss:
DHCPDiscover(build packet)
DHCPOffer(unpack packet)
DHCPRequest(build packet)
DHCPACK(unpack packet)
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
	def __init__(self):
		self.xid = generateXid()
		self.mac = generateMac()
		self.print_info()
		
	def print_info(self):
		print("[Client] send DHCP Discover packet----------------------")
		print("MAC:"+transMac(self.mac))
		print("TransationID:"+transXid(self.xid))

	def buildPacket(self):
		packet  = b''
		packet  = b'\x01'   #Message type: Boot Request (1)
		packet += b'\x01'   #Hardware type: Ethernet
		packet += b'\x06'   #Hardware address length: 6
		packet += b'\x00'   #Hops: 0 
	
		packet += self.xid       #Transaction ID
		packet += b'\x00\x00'    #Seconds elapsed: 0
		packet += b'\x80\x00'   #Bootp flags: 0x8000 (Broadcast) + reserved flags
		packet += inet_aton('0.0.0.0')    #Client IP address: 0.0.0.0
		packet += inet_aton('0.0.0.0')    #Your (client) IP address: 0.0.0.0
		packet += inet_aton('0.0.0.0')    #Next server IP address: 0.0.0.0
		packet += inet_aton('0.0.0.0')    #Relay agent IP address: 0.0.0.0
		#CHADDR(16byte)
		packet += self.mac    #Client MAC address
		packet += b'\x00' *10    #Client hardware address padding
		packet += b'\x00' * 192
	
		packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
		packet += b'\x35\x01\x01'   #Option: (t=53,l=1,value=1) DHCP Message Type = DHCP Discover
		packet += b'\x37\x03\x03\x01\x06'   #Option: (t=55,l=3) Parameter Request List
		packet += b'\xff'   #End Option
		return packet

class DHCPOffer:
	def __init__(self,data,xid,serverIP):
		self.isRecv=1
		self.xid = xid
		self.dhcpServer = ''
		self.offerIP = ''
		self.serverIP = serverIP
		self.unpack(data)
		
	def unpack(self,data):
		serverIP = '.'.join(map(lambda x:str(x), data[20:24]))
		type = int(data[242])
		if data[4:8] != self.xid or serverIP!=self.serverIP or type != OFFER:
			self.isRecv = 0
			print("[Client] receives other DHCP Offer packet")
		else:
			print("[Client] receives DHCP Offer packet---------------------")
			self.offerIP = '.'.join(map(lambda x:str(x), data[16:20]))
			self.dhcpServer = '.'.join(map(lambda x:str(x), data[263:267]))
			
			print("MAC:"+transMac(data[28:34]))
			print("TransationID:"+transXid(data[4:8]))
			print("Offer IP: " + '.'.join(map(lambda x:str(x), data[16:20])))
			print("Next Server IP: " + '.'.join(map(lambda x:str(x), data[20:24])))
			print("Subnet Mask:"  + '.'.join(map(lambda x:str(x), data[245:249])))
			print("Router:"  + '.'.join(map(lambda x:str(x), data[251:255])))
			print("lease Time:"  + str(struct.unpack('!i',data[257:261])))
			print("DHCP Server:"  + '.'.join(map(lambda x:str(x), data[263:267])))
			print("DNS server:"  + '.'.join(map(lambda x:str(x), data[269:273])))
			print("DNS server:"  + '.'.join(map(lambda x:str(x), data[275:279])))
			print("DNS server:"  + '.'.join(map(lambda x:str(x), data[281:285])))
		
class DHCPRequest:
	def __init__(self,xid,mac,serverIP,dhcpServer,offerIP):
		self.xid = xid
		self.mac = mac
		self.serverIP = serverIP
		self.dhcpServer = dhcpServer
		self.offerIP = offerIP
		self.print_info()
	def print_info(self):
		print("[Client] send DHCP Request packet-----------------------")
		print("MAC:"+transMac(self.mac))
		print("TransationID:"+transXid(self.xid))
		print("ServerIP:"+self.serverIP)
		print("OfferIP:"+self.offerIP)
		print("DHCPServer:"+self.dhcpServer)
		
	def buildPacket(self):
		packet  = b''
		packet += b'\x01'   #Message type: Boot Request (1)
		packet += b'\x01'   #Hardware type: Ethernet
		packet += b'\x06'   #Hardware address length: 6
		packet += b'\x00'   #Hops: 0 
	
		packet += self.xid       #Transaction ID
		packet += b'\x00\x00'    #Seconds elapsed: 0
		packet += b'\x00\x00'   #Bootp flags: 0x8000 (Broadcast) + reserved flags
		packet += inet_aton('0.0.0.0')    #Client IP address: 0.0.0.0
		packet += inet_aton('0.0.0.0')    #Your (client) IP address: 0.0.0.0
		packet += inet_aton(self.serverIP)    #Next server IP address: 0.0.0.0
		packet += inet_aton('0.0.0.0')    #Relay agent IP address: 0.0.0.0
		#CHADDR(16byte)
		packet += self.mac    #Client MAC address
		packet += b'\x00' *10    #Client hardware address padding
		packet += b'\x00' * 192
	
		packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
		
		packet += b'\x35\x01\x03'   #Option: (t=53,l=1,value=3) DHCP Message,DHCP Request
		packet += b'\x32\x04'   #Option: (t=50,l=4) ip requested
		packet += inet_aton(self.offerIP)
		packet += b'\x36\x04'   #Option: (t=54,l=4) DHCP Server
		packet += inet_aton(self.dhcpServer)
		packet += b'\xff'   #End Option
		return packet

class DHCPACK:

	def __init__(self,data,xid,serverIP):
		self.isRecv =1 
		self.xid = xid
		self.serverIP=serverIP
		self.unpack(data)

	def unpack(self,data):
		serverIP = '.'.join(map(lambda x:str(x), data[20:24]))
		type = int(data[242])
		if data[4:8] != self.xid or serverIP != self.serverIP or type != ACK:
			self.isRecv = 0
			print("[Client] receives other DHCP ACK")
			return

		print("[Client] receives DHCP ACK packet-----------------------")
		print("TransationID:"+transXid(data[4:8]))
		print("MAC:"+transMac(data[28:34]))
		print("Offer IP: " + '.'.join(map(lambda x:str(x), data[16:20])))
		print("Next Server IP: " + '.'.join(map(lambda x:str(x), data[20:24])))
		print("Subnet Mask:"  + '.'.join(map(lambda x:str(x), data[245:249])))
		print("Router:"  + '.'.join(map(lambda x:str(x), data[251:255])))
		print("lease Time:"  + str(struct.unpack('!i',data[257:261])))
		print("DHCP Server:"  + '.'.join(map(lambda x:str(x), data[263:267])))
		print("DNS server:"  + '.'.join(map(lambda x:str(x), data[269:273])))
		print("DNS server:"  + '.'.join(map(lambda x:str(x), data[275:279])))
		print("DNS server:"  + '.'.join(map(lambda x:str(x), data[281:285])))
		
if __name__ =='__main__':

	dhcps = socket(AF_INET, SOCK_DGRAM)
	dhcps.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) 
	dhcps.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
	serverIP = "192.168.1.1"
	try:
		dhcps.bind(('0.0.0.0', 68))
	except Exception as e:
		print(e)
		dhcps.close()
		exit()
	dhcps.settimeout(20)
	
	discoverPkt = DHCPDiscover()
	dhcps.sendto(discoverPkt.buildPacket(), ('<broadcast>', 67))
	
	try:
		while True:
			data = dhcps.recv(1024)
			offerPkt = DHCPOffer(data, discoverPkt.xid,serverIP)
			if offerPkt.isRecv == 1 :
				break
				
		requestPkt = DHCPRequest(discoverPkt.xid,discoverPkt.mac,offerPkt.serverIP,offerPkt.dhcpServer,offerPkt.offerIP)
		dhcps.sendto(requestPkt.buildPacket(),('<broadcast>',67))
		while True:
			data = dhcps.recv(1024)
			ackPacket = DHCPACK(data,discoverPkt.xid,serverIP)
			if ackPacket.isRecv == 1 :
				break
	except timeout as e:
		print(e)
	
	dhcps.close()
