#!/usr/bin/python3
#-*-encoding: utf8 -*-
import time 
import sys 
import email.utils 
import email.header 
import email.parser

class Parser:
    def decodePayload(self, part):
        payload = part.get_payload(decode=True)
        if isinstance(payload, bytes):
            types = [ ]
            if part.get_content_charset():
                types.append(part.get_content_charset())
            types += [sys.getdefaultencoding(), 'utf8', 'latin1']
            for type in types:
                try:
                    payload = payload.decode(type)
                    break
                except:
                    pass
            else:
                payload = "Error: Can not decode to Unicode"
        return payload

    def findText(self, payload):
        for part in payload.walk( ):
            if part.get_content_type( ) == 'text/plain':
                return 'text/plain', self.decodePayload(part)

        for part in payload.walk( ):
            if part.get_content_type( ) == 'text/html':
                return 'text/html', self.decodePayload(part)

        for part in payload.walk( ):
            if part.get_content_maintype( ) == 'text':
                return part.get_content_type( ), self.decodePayload(part)

        return  "text/plain", "--Error: no text to display--" 
 
    def splitAddrHeader(self, rawheader):
        pairs   = email.utils.getaddresses([rawheader])
        decoded = [ ]
        for (name, addr) in pairs:
            try:
                name = self.decodeHeader(name)
            except:
                name = None
            joined  = email.utils.formataddr((name, addr))
            decoded += [joined]
        return ", ".join([name, addr])
    
    def getAddress(self, rawheader): 
        pairs = email.utils.getaddresses([rawheader])
        for (name, addr) in pairs: 
            addr = addr 
        return addr  

    def decodeHeader(self, rawheader):
        pairs = email.header.decode_header(rawheader)
        types = [sys.getdefaultencoding(), 'big5', 'utf8', 'raw-unicode-escape']
        decoded = [ ]
        for part, enc in pairs:
            if enc == None:
                if not isinstance(part, bytes):

                    decoded += [part]
                else: 
                    for type in types: 
                        try: 
                            decoded += [part.decode(type)]
                            break  
                        except UnicodeError:
                            pass 

            else:
                for type in types:
                    try:
                        decoded += [part.decode(type)]
                        break
                    except UnicodeError:
                        pass

        return ' '.join(decoded)


    def parseHeader(self, rawheader): 
        try: 
            header = email.parser.Parser().parsestr(rawheader, headersonly=True) 
        except: 
            header = rawheader
        return header 


    def parseMessage(self, rawmessage):
        try:
            message = email.parser.Parser( ).parsestr(rawmessage)
        except:
            message = rawmessage
        return message 


    def parseDate(rawdate): 
        """
        29 Mar 2008 10:13:59 -0000 ==>> (2008, 3, 29, 10, 13, 59, 0, 1, -1)
        """ 
        date = email.utils.parsedate(rawdate) 
        return date or rawdate  

def textwrap(text, width=0, counter=0): 
    """ 
    Some other types of text may occupy more positions 
    than the letters of the alphabet this will make the 
    string beyond the "curses interface" so they have 
    the same length
    """ 
    rec   = "" 
    count = 0
    total = 0 
    for str in text.split('\n'): 
        if len(str.encode()) >= width: 
            for s in str: 
                bytes = len(s.encode( ))
                
                if bytes > 1: 
                    count += bytes * 0.7 
                    total += bytes * 0.7
                else: 
                    count += bytes 
                    

                if count >= width: 
                    rec = rec + s + '\n'
                    count = 0  
                else: 
                    rec = rec + s
            
        else: 
            rec = rec + str + '\n'
    if counter: 
        return total  
    else: 
        return '\n'.join([rec])


def HKDateFormat(date):
    thisY, thisM, toD  = time.strftime('%Y-%m-%d').split('-') 
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    y = None
    for m in month:  
        if m in date:
            index = date.split(' ').index(m) 
            d, m, y = date.split(' ')[index-1: index+2]  
            m = str(month.index(m)+1) 
            break
    if y != None: 
        if thisY == y: 
            date = '%s月' % m 
        else: 
            date = '/'.join([y, m, d])
    return date

if __name__ == '__main__': 
    prs = Parser( )
    obj = prs.parseMessage('jack')
    print(type(obj))    
    text = '''
    隕石墜落之處引發猛烈爆炸，時產生強烈氣流, 震碎多棟建築物的窗戶
    ，有工廠的幾千呎屋頂塌下而大多數人是被震碎的玻璃割傷，暫未有報
    告顯示有人被殞石碎片直接擊隕石墜落之處引發猛烈爆炸，時產werwerwes生強烈氣流, 震碎多棟建築物的窗戶
    ，有工廠的幾千呎屋頂塌下而大多fghgfhf數人是被震碎的玻璃割傷，暫未有報
    告顯示有人被殞石碎片直接擊隕石墜落之處引發猛烈爆炸，時產werwerwes生強烈氣流, 震碎多棟建築物的窗戶
    ，有工廠的幾千呎屋頂塌下而大多fghgfhf數人是被震碎的玻璃割傷，暫未有報
    告顯示有人被殞石碎片直接擊
    '''
    litters = 'A' * 100
    c = '時產werwerwes生強烈氣流, 震碎多棟建築物的窗戶，有工廠的幾千呎屋頂塌下而大多fghgfhf數人是被震碎的玻璃割'
    l = 'A'* 100
    print('%s\n%s' % (text_alignment(text, 10), text_alignment(litters, 10)))
    
    input( )