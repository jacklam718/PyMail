#!/usr/bin/python3
from email.message import Message
import poplib 
import email.header
import sys 


class Fetcher: 
    def __init__(self, servername, user, passwd, ssl=False): 
        self.servername = servername 
        self.user       = user 
        self.passwd     = passwd 
        self.ssl        = ssl 

    def Connect(self):
        if self.ssl: 
            server = poplib.POP3_SSL(self.servername, 995)
        else:
            server = poplib.POP3(self.servername, 110) 
        server.user (self.user) 
        server.pass_(self.passwd)    
        return server

    def Stat(self): 
        return self.Connect( ).stat( )  


    def decodeFullText(self, messageBytes): 
        text = None 
        types  = ['utf8', 'big5', 'ascii', 'latin1']
        #types.append(sys.getdefaultencoding()) 
        for type in types: 
            try: 
                text = [Bytes.decode(type) for Bytes in messageBytes]  
                break 
            except UnicodeError: 
                pass
        else:
            text = ['<<Mail Content>> Unknow>>']
        return text


    def downloadMessage(self, num):
        server = self.Connect( )
        try: 
            resp, message, respsz = server.retr(num) 
            message = self.decodeFullText(message)
        finally: 
            server.quit( )  
        return resp, '\n'.join(message), respsz  


    def downloadAllHeaders(self, loadfrom=1, limit=None, progress=None):
        server = self.Connect( ) 
        msgCount, respsz = server.stat( ) 
        headerSize = [ ]
        headerResp = [ ]  
        headerList = [ ] 
        try: 
            for i in range(loadfrom, msgCount): 
                if progress: progress( i )
                if limit and (i <= msgCount - limit): 
                    headerList.append('<Skiped header>') 
                else: 
                    resp, header, respsz = server.top(i, 0)
                    header = self.decodeFullText(header) 
                    headerSize.append(respsz) 
                    headerResp.append(resp) 
                    headerList.append('\n'.join(header)) 
        finally: 
            server.quit( ) 
        return headerResp, headerList, headerSize

    def downloadAllMessages(self, loadfrom=1, limit=None, progress=None): 
        server = self.Connect( )
        resp, msgCount, respsz = server.list( )
        messageSize = [int(x.split()[1]) for x in msgCount]
        messageList = [ ] 
        msgCount    = len(msgCount)
        try: 
            for i in range(loadfrom, msgCount):
                if progress: progress( i ) 
                if limit and (i <= msgCount-limit):  
                    messageList.append('<Skiped message>')
                
                else: 
                    resp, message, respsz = server.retr(i)
                    message = self.decodeFullText(message) 
                    messageList.append('\n'.join(message)) 
        finally: 
            server.quit( ) 
        return resp, messageList, messageSize


    def delete(self, num): 
        server = self.Connect( )
        try: 
            deleteMsg = server.dele(num) 
        finally: 
            server.quit( ) 
        return deleteMsg 





if __name__ == '__main__': 
    getmail = Fetcher
    for i in [300]:
        size, header, octets = getmail.downloadHeader(i, ['From', 'Subject', 'Date'])
        print('')
        for h in header: print(h)

    input('Press enter exit!') 