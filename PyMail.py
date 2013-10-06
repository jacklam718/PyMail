#!/usr/bin/python3 
import curses 
import sys 
from curses      import textpad 
from Progressbar import Progressbar 
from cursDialog  import * 
from mailFetcher import Fetcher
from mailParser  import Parser, textwrap 

messageDict = { }

EXIT     = 0
CONTINUE = 1 

FOCUS    = curses.A_BOLD | curses.A_STANDOUT 
NO_FOCUS = curses.A_NORMAL

tmpencode= 'utf8'


class Mailbox(Fetcher):
    UP    = -1 
    DOWN  =  1
    MARKING   = curses.A_STANDOUT 
    NO_MARKING= curses.A_NORMAL  
    def __init__(self, servername, user, password, ssl=False): 
        Fetcher.__init__(self, servername, user, password, ssl)  
        self.win = curses.newwin(y-1, x, 1, 0)
        self.y, self.x  = self.win.getmaxyx( ) 
        self.WIN_LINES  = curses.LINES - 3
        self.topLineNum       = 0
        self.highlightLineNum = 0
        self.markedLineNum    = [ ]
        self.makeFrame ( )                    
        self.makePreviewMessageWin( )
        #self.loadAllHeaders( )  
        self.loadAllMessages( )
    
    # Make main Frame use rectangle
    def makeFrame(self):
        Y, X = self.y, self.x
        # Index listbox 
        hight, width = Y-1, 34
        y, x = 0, 0
        self.win.attrset(color_red | curses.A_BOLD)
        rectangle(self.win, y, x, hight+y, width+x) 
        
        # titlebox 
        hight, width = 3, X-36
        y, x = 0, 35
        self.win.attrset(color_blue | curses.A_BOLD) 
        rectangle(self.win, y, x, hight+y, width+x) 
        
        # draw preview box
        hight, width = self.y-5, self.x-36 
        y, x = 4, 35
        rectangle(self.win, y, x, hight+y, width+x) 
        
        # set go back to normal color and normal attr
        self.win.attrset(color_normal | curses.A_NORMAL)
        self.win.refresh( )


    def makePreviewMessageWin(self):
        hight, width = self.y-6, self.x-37
        self.prewin = self.win.subwin(hight, width, 6, 36)


    def makeRectangle(self, win, lines, cols, hight, width): 
        #Y, X = maxy, 
        hight, width = hight, width 
        win.attrset(color_blue | curses.A_BOLD)

        #def rectangle(win, lines, cols, hight, width):
        try: 
            win.vline(lines+1, cols,   curses.ACS_VLINE, hight - lines - 1)
            win.hline(lines,   cols+1, curses.ACS_HLINE, width - cols  - 1)
            win.hline(hight,   cols+1, curses.ACS_HLINE, width - cols  - 1)
            win.vline(lines+1, width,  curses.ACS_VLINE, hight - lines - 1)
            win.addch(lines,   cols,   curses.ACS_ULCORNER)
            win.addch(lines,   width,  curses.ACS_URCORNER)
            win.addch(hight,   cols,   curses.ACS_LLCORNER)
            win.addch(hight,   width,  curses.ACS_LRCORNER)
        except curses.error: 
            pass  
    
        y, x = 0, 0 
        #rectangle(win, y, x, hight+y, width+x)
        # set go back to color normal and attr normal
        win.attrset(color_normal | curses.A_NORMAL)
        win.refresh( )

       
    def markLine(self): 
        marklinenum = self.highlightLineNum + self.topLineNum 
        if marklinenum in self.markedLineNum: 
            self.markedLineNum.remove(marklinenum) 
        else: 
            self.markedLineNum.append(marklinenum) 

    def getAllHeaders(self):
        msgCount = self.Stat( )[0] 
        pb = Progressbar(msgCount, title="J'MAIL", message="Downloading headers...", clr1=color_red, clr2=color_green, y=y, x=x)
        loadfrom = 1
        limit    = None
        '''
        loadfrom = config['loadfrom']  
        limit    = config['limit']
        '''
        return self.downloadAllHeaders(loadfrom, limit, pb.progress) 

    def getAllMessages(self):
        msgCount = self.Stat( )[0]  
        pb = Progressbar(msgCount, title="J'MAIL", message="Downloading messages...", clr1=color_red, clr2=color_green, y=y, x=x)
        loadfrom = 1
        limit    = None
        '''
        loadfrom = config['loadfrom']  
        limit    = config['limit']
        '''
        return self.downloadAllMessages(loadfrom, limit, pb.progress)

    def loadAllHeaders(self): 
        resp, headerList, headerSize = self.getAllHeaders( )
        parser = Parser( ) 
        headerList = [ parser.parseHeader ( header ) for header in headerList ] 
        headerList = [ parser.splitAddrHeader( header.get('From', '<Unknow>')) for header in headerList ]
        self.headerLine = [hdr[:30].rstrip() for hdr in headerList] 
        self.outputLineNum = len(self.headerLine) 

    def loadAllMessages(self, num=None):
        resp, messageList, messageSize = self.getAllMessages( )
        parser = Parser( ) 
        headerList = [ parser.parseHeader( header ) for header in messageList] 
        fromList   = [ parser.splitAddrHeader( header.get("From",    "<Unknow>") ) for header in headerList ]
        toList     = [ parser.splitAddrHeader( header.get("To",      "<Unknow>") ) for header in headerList ]  
        subjList   = [ parser.decodeHeader   ( header.get("Subject", "<Unknow>") ) for header in headerList ]  
        dateList   = [ header.get( "Date",   "<Unknow>" ) for header in headerList ] 
        #dateList   = [ parser.paseDate(header.get("Date",    "<Unknow>")) for header in headerList]
        self.indexList = [hdr[:33].rstrip() for hdr in fromList]   
        self.indexList.reverse( ) 
        self.outputLineNum = len(self.indexList) 
        
        messageList = [ parser.parseMessage( message ) for message in messageList ]
        messageList = [ parser.findText( message )[1]  for message in messageList ]    
        
        count = self.outputLineNum
        for (subj, frm, to, date, msg) in zip( subjList, fromList, toList, dateList, messageList ):
            messageDict[ count ]  = [subj, frm, to, date, msg] 
            count -= 1 

    def refreshMailbox(self):
        self.win.erase( )
        top    = self.topLineNum
        bottom = self.topLineNum + self.WIN_LINES
        
        for (index, line) in enumerate(self.indexList[top:bottom]):
            linenum = self.topLineNum + index 
            if linenum in self.markedLineNum: 
                marking = self.MARKING
            else: 
                marking = self.NO_MARKING   
            try: 
                if index == self.highlightLineNum: 
                    subj, frm, to, date, msg = messageDict[ linenum+1 ]
                    msg  = textwrap(text=msg,  width=self.x-36)
                   
                    # Hightlight current line 
                    self.win.addstr(index+1, 1, line[:28], marking | curses.A_BOLD | curses.A_STANDOUT)

                    self.win.addstr(1, 36, subj.rstrip()[0:self.x-40])
                    self.win.addstr(2, 36, date)

                    for (i, msg) in enumerate(msg.split('\n')[:self.y-7]): 
                        self.prewin.addstr(i, 0, msg)
                    
                    cur_line = '%d / %d' % (linenum+1, len(messageDict.keys()))
                    self.win.addstr(y-3, int((x-2)-len(cur_line)), cur_line, color_green | curses.A_BOLD)
                else:
                    self.win.addstr(index+1, 1, line[:28], marking)
            except: 
                self.win.addstr(0, 60, 'Error') 
        self.makeFrame( )
        self.prewin.refresh( ) 

    def Scolling_Text(self, win, text, top, bottom, y, x):
        textlines = len(text) 
        while True: 
            win.erase( )  
            
            for (i, lines) in enumerate(text[top:bottom]): 
                win.addstr(i, 0, lines)
            cur_line = "%d - %d / %d" % (top+1, top+i+1, textlines) 
            win.addstr(y-1, x-len(cur_line)-1, cur_line, color_green | curses.A_BOLD) 
            win.refresh( )
            key = screen.getch( )
            if key == curses.KEY_UP and top != 0: 
                top    += self.UP 
                bottom += self.UP 
            elif key == curses.KEY_DOWN and bottom < textlines:
                top    += self.DOWN 
                bottom += self.DOWN 
            elif key == curses.KEY_LEFT: 
                TopbarMailbox( ).left_right(-1) 
            elif key == curses.KEY_RIGHT: 
                TopbarMailbox( ).left_right(1 ) 
            elif key == ord('q'): break 


    def displayMessage(self, otherMsg=None): 
        #self.makeRectangle(self.win, self.y, self.x)
        self.win.clear( )

        # Header frame 
        self.makeRectangle(self.win, lines=0, cols=0, hight=5,  width=self.x-1)

        # Message frame
        self.makeRectangle(self.win, lines=6, cols=0, hight=self.y-1, width=self.x-1)

        win  = self.win 
        #Y, X = self.y, self.x 
        hight, width = self.y-8, self.x-2
        msgnum = self.topLineNum + self.highlightLineNum + 1 
        
        # get subject, from, date, message to display
        if not otherMsg: 
            subj, frm, to, date, msg = messageDict.get(msgnum, 'Error')
        else: 
            subj, frm, to, date, msg = 'None', 'None', 'None', 'None', otherMsg
        msg      = textwrap(text=msg, width=width).split('\n')  
        
        win.addstr(1, 1, 'Subject: %s' % subj.strip( )[0:self.x-12])
        win.addstr(2, 1, 'From   : %s' % frm.strip( ) [0:self.x-9]) 
        win.addstr(3, 1, 'To     : %s' % to.strip( )  [0:self.x-9]) 
        win.addstr(4, 1, 'Date   : %s' % date.strip( )[0:self.x-9])
        win.refresh( )  
        
        subw  = curses.newwin(hight, width, 8, 1)
        
        top      = 0
        bottom   = hight-1

        self.Scolling_Text(win=subw, text=msg, top=0, bottom=hight-1, y=hight, x=width)

    # Scrolling index
    def up_down(self, increment): 
        nextlinenum = self.highlightLineNum + increment  
        if increment == self.UP and ( self.topLineNum != 0 and self.highlightLineNum == 0 ): 
            self.topLineNum += self.UP
            return  
        elif increment == self.DOWN and ( self.topLineNum+self.WIN_LINES ) != self.outputLineNum and nextlinenum == self.WIN_LINES:   
            self.topLineNum += self.DOWN
            return 
        if increment == self.UP and ( self.topLineNum != 0 or self.highlightLineNum != 0 ):
            self.highlightLineNum = nextlinenum 
        elif increment == self.DOWN and ( self.topLineNum+self.WIN_LINES)+1 != self.outputLineNum and nextlinenum != self.WIN_LINES:
            self.highlightLineNum = nextlinenum 

    

class TopbarMailbox(Mailbox):
    LEFT  = -1 
    RIGHT =  1
    def __init__(self, servername, user, password, ssl=False):
        self.topbar = screen
        self.focus = 0 
        self.makeTopbar( )
        Mailbox.__init__(self, servername, user, password, ssl) 

    def makeTopbar(self): 
        space = 2 
        self.display_pos = [ ] 
        self.menufunc = ('Compose', 'Save', 'Delete', 'Find', 'Forward', 'Reply', 'Translate', 'Option', 'Help')
        self.topbar.addstr(0, 0, ' '*x, curses.A_STANDOUT | curses.A_BOLD)      
        for f in self.menufunc: 
            self.topbar.addstr(0, space,   f[0],  curses.A_STANDOUT | curses.A_BOLD | curses.A_UNDERLINE  )
            self.topbar.addstr(0, space+1, f[1:], curses.A_STANDOUT | curses.A_BOLD)  
            self.display_pos.append(space) 
            space = space + len(f) + 2 
        self.topbar.addstr(0, x-10, "J'MAIL 0.1", curses.A_STANDOUT)     
        self.topbar.refresh( )

    # Just draw a mail compose window 


    '''
    def composeWin(self): 
        win = self.topbar; Y, X = self.y, self.x
        hight, width = 5, X-1 
        y, x = 0, 0
        rectangle(win, y, x, hight+y, width+x)

        hight, width = Y-5, X-1
        y, x = Y-hight, 0
        rectangle(win, y, x, hight+y, width+x)
        win.refresh( )
        win.getch( ) 
    '''
    def composeWin(self): 
        self.makeRectangle(self.topbar, self.y+1, self.x)
        self.win.getch( )

    def Compose(self): 
        self.composeWin( ) 
        

    def callfunc(self): 
        funcdict= {1: 'Compose( )',  2: 'Save( )' ,   3: 'Delete( )', 
                   4: 'Find( )',     5: 'Forward( )', 6: 'Reply( )', 
                   7: 'Translate( )',8: 'Option( )',  9: 'Help( )' } 
        eval('self.'+funcdict[self.focus+1]) 

    def Delete(self):
        deleMsg = None
        msgnumList = self.markedLineNum
        if not msgnumList:
            showmessage(title='Delete message', message='Please use space key to mark message line')
            return None 
        else:
            if askyescancel(title='Delete message', message='Are you want delete message?'):
                for num in  msgnumList: 
                    deleMsg = self.delete(num)
        return deleMsg or None

    def Fine(self): 
        pass 

    def Forward(self): 
        pass 
        subj, frm, to, date, msg

    def Reply(self): 
        linenum = self.topLineNum + self.hightlightLineNum + 1 
        addr = messageDict[ linenum ] 
        addr = Parser( ).getAddress(addr) 


    def Save(self):  
        savepath = askfilesave(title='Save message', message='Please input save path or use default directory')
        if savepath:  
            try: 
                msgnum   = self.topLineNum + self.highlightLineNum + 1
                subj, frm, to, date, msg = messageDict[msgnum]
                filename = os.path.join(savepath, frm) 
                fullmsg  = 'Subject:%s\nFrom   :%s\nTo     :%s\nDate   :%s\n%s\n%s' % ( subj, frm, to, date, '-'*80, msg )
                file = open(filename, 'w', encoding='utf8').write(fullmsg)  
            except: 
                err  = sys.exc_info()[1] 
                info = 'File name : %s\nError type: %s\n\n%s' % (err.filename, err.strerror, 'Please input again')
                showmessage(title='Save fail', message=info)
                self.Save( ) 


    def Translate(self): 
        import urllib.request 
        from ParserHtml import TranslateParser 
        url = 'http://translate.google.com.hk'
        query_args = urllib.parse.urlencode({'hl': 'zh-TW', 'ie': 'utf8', 'text': text, 'langpair': 'en|zh-TW'}) 
        query_args = query_args.encode('utf8') 
        request = urllib.request.Request(url, query_args)
        request.add_header('User-agent', 'Mozilla/4.0 (Compatible; MSIE 7.0; Windows NT)') 
        respont_html = urllib.request.urlopen(request) 

        text = TranslateParser(respont_html) 
        return text 


    def Option(self): 
        pass 

    def Help(self): 
        
        rectangle(self.win, 20, 20, self.y, self.x)
        win = self.win
        win.refresh( )
        win.getch( )



        introductionMsg = """
Developer 〄: Jack Lam
Email     ✉ : jacklam718@gmail.com
Version   ✍ : 0.10  

--------------------------------------------------------------------
Thank you use the ( J'MAIL ) Program. 
I'm Python Beginner so. this program is only basic simple functions.   
If you have nay comments about this program or you would like to add
me as a fiend also can to contact me.

Else: If you think this source code is useful I also welcome you use it.  

Thank you so much.


感謝您使用（J'MAIL）程序,
我是Python的初學者, 這個程序是只有基本的簡單功能。
如果你有什麼關於此程序的意見，或者您想添加
我作為一個朋友，也可以與我聯繫。

還有: 如果您認為此源代碼有用也非常歡迎你使用

非常感謝您。
""".lstrip( )
        #self.displayMessage(otherMsg=introductionMsg)

    def Exit(self): 
        pass 


    def textEdit(self):
        win   = self.win; Y, X = self.y, self.x 
        hight, width = Y-8, X-2
        subw  = curses.newwin(hight, width, 8, 1)
    

    def refreshTopbar(self): 
        self.makeTopbar( )
        self.topbar.addstr(0, self.display_pos[self.focus],   self.menufunc[self.focus][0],  )#curses.A_BOLD | curses.A_UNDERLINE)
        self.topbar.addstr(0, self.display_pos[self.focus]+1, self.menufunc[self.focus][1:], )#curses.A_BOLD)
        self.topbar.refresh( )      

    def left_right(self, increment):
        if increment == self.LEFT and self.focus !=  0:
            self.focus += self.LEFT
        elif increment == self.RIGHT and self.focus != len(self.menufunc)-1: 
            self.focus += self.RIGHT

    def __call__(self):  
        select = self.focus 
        # Test 
        screen.addstr(23, 50, 'Topbar Function call: %s' % select)
        screen.refresh( )  
        #return eval(TARBAR_dict[select]) 

def rectangle(win, lines, cols, hight, width):
    try: 
        win.vline(lines+1, cols,   curses.ACS_VLINE, hight - lines - 1)
        win.hline(lines,   cols+1, curses.ACS_HLINE, width - cols  - 1)
        win.hline(hight,   cols+1, curses.ACS_HLINE, width - cols  - 1)
        win.vline(lines+1, width,  curses.ACS_VLINE, hight - lines - 1)
        win.addch(lines,   cols,   curses.ACS_ULCORNER)
        win.addch(lines,   width,  curses.ACS_URCORNER)
        win.addch(hight,   cols,   curses.ACS_LLCORNER)
        win.addch(hight,   width,  curses.ACS_LRCORNER)
    except curses.error: 
        pass    


def keyHandler(tbmbox, KeyRecord=[]):
    key = screen.getch( )
    # remember recent key 
    if key in (258, 259, 260, 261): KeyRecord.append(key)
    try:    
        RecentKey = KeyRecord[0]
    except IndexError: 
        RecentKey = curses.KEY_DOWN
    if len(KeyRecord) == 2: KeyRecord.remove(RecentKey)

    # for key Up and Down
    if key == curses.KEY_UP: 
        tbmbox.up_down(-1) 
    elif key == curses.KEY_DOWN: 
        tbmbox.up_down( 1 )  
         
    # for key Left and Right 
    elif key == curses.KEY_LEFT:
        tbmbox.left_right(-1) 
    elif key == curses.KEY_RIGHT:
        tbmbox.left_right( 1 )
        
    if key == ord('\n') and RecentKey in (curses.KEY_UP, curses.KEY_DOWN): 
        tbmbox.displayMessage( )
        
    elif key == ord('\n') and RecentKey in (curses.KEY_LEFT, curses.KEY_RIGHT): 
        tbmbox.callfunc( )
        
    # for space key to mark message 
    elif key == 32: 
        tbmbox.markLine( )

    # for exit key  
    elif key == 27: 
        return False 
    return True   


def Main(stdscr): 
    global screen, color_red, color_green, color_blue, color_normal, y, x 
    screen  = stdscr

    screen.keypad(True) 
    curses.noecho( ) 
    curses.cbreak( )
    y, x = screen.getmaxyx( )

    # setting colors  
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0) 
    curses.init_pair(1, curses.COLOR_RED,   -1) 
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE,  -1) 
    curses.init_pair(4, -1, -1) 
    color_red    = curses.color_pair(1) 
    color_green  = curses.color_pair(2) 
    color_blue   = curses.color_pair(3)
    color_normal = curses.color_pair(4) 


    tbmbox = TopbarMailbox
    
    while True: 
        tbmbox.refreshMailbox( )
        tbmbox.refreshTopbar ( ) 
        keyHandler(tbmbox)
        curses.curs_set(1)


if __name__ == '__main__': 
    import os 
    os.system('resize -s 32 115') 
    curses.wrapper(Main)
    
