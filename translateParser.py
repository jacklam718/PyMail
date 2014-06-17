#!/usr/bin/python3
# --*-- coding: utf-8 --*--

from html.parser import HTMLParser 

class GoogleTransParser(HTMLParser):
	def __init__(self, strict=False): 
		HTMLParser.__init__(self, strict) 
		self.text = '' 
		self.save = False 
		self.last = '' 

	def addtext(self, text): 
		if self.save: 
			self.text += text 
			self.last =  text 

	def textwrap(self, force=False): 
		if force or self.last != '\n': 
			self.addtext('\n') 

	def handle_starttag(self, tag, attrs):
		if tag == 'span' and ('id', 'result_box') in attrs: 
			self.save = True 
 
		elif tag == 'td':
			self.textwrap( )
		elif tag == 'br': 
			self.textwrap(True) 
		elif tag == 'a': 
			alts = [pair for pair in attrs if 'alt' in pair]
			if alts: 
				name, value = alts[0] 
				self.addtext('[%s]' % value.replace('\n', '')) 

	def handle_endtag(self, tag): 
		if tag in ('p', 'div', 'table', 'h1', 'h2', 'li'): 
			self.save = False
			self.textwrap( ) 

	def handle_data(self, data): 
		data = data.replace('\n', '') 
		data = data.replace('\t', '') 
		if data != ' ' * len(data):  
			self.addtext(data)

	def handle_entityref(self, name): 
		xlate = dict(lt='<', gt='>', amp='&', nsbp='').get(name, '?') 
		if xlate: 
			self.addtext(xlate) 

def TranslateParser(html, strict=False): 
	p = GoogleTransParser(strict); p.feed(html); return p.text
