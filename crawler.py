#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib3
import re
from urllib.parse import urlparse, urljoin
from time import sleep, time
from random import randint
from argparse import ArgumentParser
import json
import urllib.robotparser
import sqlite3
import datetime

class Crawler:
	"""
		:host the root of the website
		:delay_func the function to call to simulate the human activity
	"""
	def __init__(self, host, timeout, delay):
		# It represent the current webpage
		self.url = '/'
		# it represent the url to craw
		self.url_to_crawl = [self.url]
		# We create an ConnectionPool instance of its host.
		self.conn = urllib3.connection_from_url(host)
		# It represent the current data while the crawling
		self.content = b''
		self.MAX_SIZE_PER_PAGE = 1024*256 # 256Kb
		# We build a regular expression to get url link in a text
		self.HTML_TAG_REGEX = re.compile(r'<a[^<>]+?href=([\'\"])(.*?)\1', re.IGNORECASE)
		self.HTML_OUTER_REGEX = re.compile(r'>(.*?)<', re.IGNORECASE)
		self.SITEMAP_TAG_REGEX = re.compile(r'<loc>(.*?)</loc>', re.IGNORECASE)
		# We set the robotparser
		self.ROBOT_PARSER = urllib.robotparser.RobotFileParser(urljoin(host, 'robots.txt'))
		# We set the user agent
		self.USER_AGENT = "Codexbot"
		self.HEADERS = {
			"User-Agent": self.USER_AGENT,
			"Accept": "text/html",
		}
		#
		self.delay = self.ROBOT_PARSER.crawl_delay(self.USER_AGENT)
		self.wait = lambda:sleep(self.delay if self.delay else delay)
		self.timeout = timeout
		# Output file of the logging
		self.logstream = open('%s_%s.log' % (self.conn.host, time()), 'a')
		self.logstream.write('HOST: %s\n' % self.conn.host)
		
		# Output of results
		self.db_conn = sqlite3.connect('%s_%s.sqlite3'%(self.conn.host, time()))
		self.db_conn.execute("CREATE TABLE IF NOT EXISTS webpages (id INTEGER PRIMARY KEY AUTOINCREMENT, host VARCHAR(255), url VARCHAR(255), data TEXT, period TIMESTAMP)")
		self.to_ignore = []
	# This method permit to read the sitemaps and get the urls inside
	def getUrlFromSiteMap(self):
		for sitemap in self.ROBOT_PARSER.sitemaps:
			r = self.conn.request('GET', urlparse(sitemap).path, preload_content=False, headers=self.HEADERS, timeout=self.timeout)
			resp = r.read(self.MAX_SIZE_PER_PAGE, decode_content=True).decode()
			for url in self.SITEMAP_TAG_REGEX.findall(resp):
				self.url_to_crawl.append(urlparse(url).path)

	# This method permit to get the content of a webpage
	def getContent(self):
		print('[INFO] Getting content from %s ...' % self.url, file=self.logstream)
		self.content = ''
		
		try:
			r = self.conn.request('GET', self.url, preload_content=False, headers=self.HEADERS, timeout=self.timeout)
		except urllib3.exceptions.MaxRetryError:
			print('[WARNING] Max retry exceed for %s, no content got' % self.url, file=self.logstream)
		except urllib3.exceptions.ReadTimeoutError:
			print('[WARNING] Timeout exceed for %s, no content got' % self.url, file=self.logstream)
		except urllib3.exceptions.HostChangedError:
			print('[WARNING] Host Changed for %s, no content got' % self.url, file=self.logstream)
		except urllib3.exceptions.ProtocolError:
			print('[WARNING] Connection broken for %s, no content got' % self.url, file=self.logstream)
		except Exception as e:
			print('[ERROR] %s for %s' % (e, self.url), file=self.logstream)
		else:
			content_length = r.headers.get('Content-Length', 0)
			content_type = r.headers.get('Content-type', "unknowed")
			# We verify if the request has succeed
			if r.status != 200:
				if r.status == 404:
					# It's possible that an URL catched not exists
					print("[ERROR] [%s]: %s" % (r.status, self.url), file=self.logstream)
				else:
					print('[CRITICAL] CODE %s not managed, %s' % (r.status, self.url), file=self.logstream)
			# We get only text file
			elif content_type.startswith('text/') and int(content_length) < self.MAX_SIZE_PER_PAGE:
				# We decode the response
				try:
					self.content = r.read(self.MAX_SIZE_PER_PAGE, decode_content=True).decode()
				except urllib3.exceptions.ReadTimeoutError:
					print("[WARNING] Read timed out for %s" % self.url, file=self.logstream)
				except UnicodeDecodeError:
					print('[CRITICAL] Decoding of %s failed, type: %s' % (self.url, content_type), file=self.logstream)

			else:
				print('[WARNING] Content of %s ignored %s' % (self.url, [content_type, content_length]), file=self.logstream)

	# This method permit to get the url links present in the webpage
	def getUrlLinks(self):
		print('[INFO] Getting urls from %s ...' % self.url, file=self.logstream)
		
		for i in self.HTML_TAG_REGEX.findall(self.content):
			url = urlparse(i[1])
			#print(self.url, i[1], url)
			
			# scheme://netloc... (root path)
			# We verify the structure of the url and if it is valid
			# eg: http://exemple.com/a/b/c
			if url.scheme:
				
				if url.netloc.replace('www.', '') == self.conn.host.replace('www.', ''):
					self.url_to_crawl.append(urljoin('/', url.path + '?' + url.query))
				else:
					print('[DEBUG] %s not belong %s...' % (i[1], self.conn.host), file=self.logstream)
			# path
			# eg: /a/b/c
			else:
				
				# //path (root path)
				# eg: //a/b/c
				if url.netloc:
					# We build and add the url
					self.url_to_crawl.append(urljoin('/' + url.netloc, url.path + '?' + url.query))
				else:
					# /path (root or sub path)
					# eg: /a/b/c a/b/c a/b/c.d
					self.url_to_crawl.append(urljoin(self.url, url.path + '?' + url.query))

	# This method permit to get the text in the webpage
	def getData(self):
		print('[INFO] Getting data from %s ...' % self.url, file=self.logstream)
		
		return self.content

	# This method start the crawling
	def start(self):
		print('[INFO] Crawling launched of %s ...' % self.conn.host, file=self.logstream)
		
		print('[INFO] Reading of the robots.txt ...', file=self.logstream)
		# We load the robots.txt
		try:
			self.ROBOT_PARSER.read()
		except urllib.error.URLError:
			print('[ERROR] Failed to read the robots.txt', file=self.logstream)
			return

		print('[INFO] Loading of the sitemaps ...', file=self.logstream)
		# We read the sitemap if present in the robots.txt
		try:
			self.getUrlFromSiteMap()
		except urllib3.exceptions.ReadTimeoutError:
			print("[WARNING] ReadTimeoutError while the getting of url from sitemap", file=self.logstream)
		
		while self.url_to_crawl:
			self.wait()

			# We get the first url
			self.url = self.url_to_crawl.pop(0)

			# We verify if url not already used or not empty
			if not self.url or self.url in self.to_ignore:
				continue	# This method permit to get the u
			# We verify if our robot can is allowed to fetch this url
			elif self.ROBOT_PARSER.can_fetch(self.USER_AGENT, self.url):
				print('[DEBUG] Crawling launched on %s ...' % self.url, file=self.logstream)
				self.getContent()
				# We save the data
				self.db_conn.execute(
					"INSERT INTO webpages (id, host, url, data, period) VALUES (?, ?, ?, ?, ?)",
					(None, self.conn.host, self.url, self.getData(), datetime.datetime.now())
				)
				self.db_conn.commit()
				self.getUrlLinks()
			else:
				print("[WARNING] We aren't allowed to fetch the url %s" % self.url, file=self.logstream)

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('HOST', help='Eg: http://example.com')
	parser.add_argument('-t', '--timeout', type=float, default=2, help='It represent the timeout')
	parser.add_argument('-s', '--delay', type=float, default=1, help='This delay will be used if no delay specified by the robots.txt')
	args = parser.parse_args()
	Crawler(
		args.HOST,
		timeout=args.timeout,
		delay=args.delay,
	).start()