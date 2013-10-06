#-*-encoding: utf8 -*-
#!/usr/bin/python3.3
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
	

if __name__ == '__main__': 
	import urllib.request, sys, textwrap

	text = ' '.join(sys.argv[1:])
	if text == '': 
		text = '''
Here is a reproduction of the legendary game Counter-Strike directly into your browser. 
You can play as a singleplayer, playing with bots, or as a multiplayer. There are several 
modes, as for example DeathMatch, Matrix mode, Zombie mode, Survival and more.In addition, 
you can choose servers according to the continent. The best is of course to play in your 
continent, where the pings are quite small. And one more piece of advice for you: if you 
have full HD, turn off the highest quality or you could experience some problems with 
the graphics. For playing you will need Unity Web Player.
''' 
	#text = open('/home/jack/weijr, tzerjen@gmail.com', 'r').read( )

	url  = 'http://translate.google.com.hk'
	query_args = {'hl': 'zh-TW', 'ie': 'utf8', 'text': text, 'langpair': 'en|zh-TW'}; query_args = urllib.parse.urlencode(query_args)
	query_args = query_args.encode('utf8') 
	request = urllib.request.Request(url, query_args) 
	request.add_header('User-agent', 'Mozilla/4.0 (Compatible; MSIE 7.0; Windows NT)')
	html = urllib.request.urlopen(request).read( ).decode('utf8')
	#print(resp)



	
	rule = textwrap.TextWrapper(60) 
	print(rule.fill(text))
	print('-'*70) 
	rule = textwrap.TextWrapper(30) 
	print(rule.fill(TranslateParser(html)))
	