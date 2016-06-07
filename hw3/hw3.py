#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter11/rscrape1.py
# Recursive scraper built using the Requests library.

import argparse, requests
from urllib.parse import urljoin, urlsplit
from lxml import etree
import re
mail={}
error =0
error_list=[]
def GET(url):
	global mail,error,error_list
	response = requests.get(url)
	if response.headers.get('Content-Type', '').split(';')[0] != 'text/html':
		error+=1
		error_list.append(url)
		return
	text = response.text
	try:
		html = etree.HTML(text)
	except Exception as e:
		print('    {}: {}'.format(e.__class__.__name__, e))
		return
	except XMLSyntaxError as e:
		print(e)
	links = html.findall('.//a[@href]')
	if not url in mail:
		mail[url]=[]

	mail[url].append(re.findall(r"[A-Za-z]+[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",text))
	for link in links:
		yield GET, urljoin(url, link.attrib['href'])

def scrape(start, url_filter):
	further_work = {start}
	already_seen = {start}
	run=0

	while further_work:
		call_tuple = further_work.pop()
		#print (call_tuple)
		function, url, *etc = call_tuple
		#print(function.__name__, url, *etc)
		for call_tuple in function(url, *etc):
			if call_tuple in already_seen:
				continue
			already_seen.add(call_tuple)
			function, url, *etc = call_tuple
			if not url_filter(url):
				continue
			further_work.add(call_tuple)
		run+=1
		if run>=20:
			break
def main(GET):
	global mail,error,error_list
	parser = argparse.ArgumentParser(description='Scrape a simple site.')
	parser.add_argument('url', help='the URL at which to begin')
	start_url = parser.parse_args().url
	starting_netloc = urlsplit(start_url).netloc
	url_filter = (lambda url: urlsplit(url).netloc == starting_netloc)
	scrape((GET, start_url), url_filter)
	print ("\n\nresult--------------------------------\nerror:%d" %(error))
	count = 1;
	for url in error_list:
		print(url)
	print("\n")
	for url in mail:
		print("[%d]url:%s" %(count,url))
		data = mail[url][0]
		if data:
			tmp = []
			for val in data:
				
				if not val in tmp:
					print (val)
				tmp.append(val)
			
		else:
			print("None")
		print ("")
		count+=1
		#print("url%s\nmail:" %(url))
		#print(mail[url])
if __name__ == '__main__':
	main(GET)
