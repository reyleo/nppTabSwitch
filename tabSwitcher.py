from Tkinter import *
import tkFont
import ctypes
from ctypes import byref, Structure, wintypes
from ctypes.wintypes import BOOL, HWND, LPARAM, LONG

class RECT(Structure):
    _fields_ = [
            ('left',   wintypes.LONG ),
            ('top',    wintypes.LONG ),
            ('right',  wintypes.LONG ),
            ('bottom', wintypes.LONG )
        ]
 
    x = property(lambda self: self.left)
    y = property(lambda self: self.top)
    w = property(lambda self: self.right-self.left)
    h = property(lambda self: self.bottom-self.top)

class TabSwitcher():

    def __init__(self):

        self.root = Tk()
        self.nppHwnd = ctypes.windll.user32.FindWindowW(u'Notepad++', None)
        #console.write('N++ HWND=' + "0x{:02x}".format(self.nppHwnd) + '\n')
        #self.tabHwnd = ctypes.windll.user32.FindWindowExA(self.nppHwnd, None, 'SysTabControl32', None)
        #console.write('Tab HWND=' + "0x{:02x}".format(self.tabHwnd) + '\n')
        if self.nppHwnd != 0 :
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(self.nppHwnd, byref(rect))
            #console.write('RECT: x=' + str(win_rect.x))
            w = 600
            x = (rect.w - w)/2 + rect.x
            h = 400
            y = (rect.h - h)/2 + rect.y            
            geom = '%dx%d+%d+%d' % (w, h, x, y)
            console.write(geom + '\n')
            console.write('top:%d left:%d right:%d bottom:%d' % (rect.top, rect.left, rect.right, rect.bottom) + '\n')
            self.root.geometry(geom)
            #self.root.geometry("600x300+-600+0")

        self.root.lift()
        self.root.attributes('-topmost',True)
        #self.root.after_idle(self.root.attributes, '-topmost',False)
        #self.root.minsize(600, 20)
        self.root.overrideredirect(1)
        self.root.wm_attributes('-alpha', 0.9)
        self.root.configure(background='black')

        # font
        self.font = tkFont.Font(root=self.root, family='Calibri', size=14)


        self.root.bind('<Escape>', self.quit)

        self.frame = Frame(self.root, bg='gray8')
        self.frame.pack(expand=True, fill=BOTH)

        # Search
        self.searchVar = StringVar()
        self.searchVar.trace('w', self.filter)
        self.search = Entry(self.frame, textvariable = self.searchVar, bg='black', fg='gray90', font=self.font, 
            insertbackground='gray90', highlightcolor='green', highlightbackground='black', highlightthickness=1, relief='flat')# relief='flat'
        #self.search.config(selectbackground='SpringGreen2', highlightthickness=3)
        self.search.pack(expand=False, fill=X)
        self.search.bind('<Down>', self.down)
        
        # List
        self.fileList = Listbox(self.frame, activestyle='none', bg='gray8', fg='gray80', selectbackground='gray16', selectforeground='gray80', font= self.font, highlightthickness=0)
        self.list = notepad.getFiles()
        self.fill()
        self.fileList.bind('<Return>', self.go)
        self.fileList.pack(expand=True, fill=BOTH)
        
        self.filtered = []

        self.root.focus_force()
        self.search.focus()
        self.root.mainloop()

    def down(self, event):
        self.fileList.select_set(0)
        self.fileList.focus()
        
    def go(self, event):
        selected = self.fileList.curselection()
        #console.write('Enter pressed. Selected = ' + ','.join(list(map(str, selected))) + '\n')
        if len(selected) == 0: return
        selIndex = selected[0]
        tab = self.list[selIndex] if len(self.filtered)==0 else self.filtered[selIndex]
        notepad.activateBufferID(tab[1])
        self.quit()
        
    def quit(self, *args):
        self.root.destroy()
        
    def fill(self):
        self.fileList.delete(0,END)
        for tab in self.list: self.fileList.insert(END, tab[0])
    
    def filter(self, *args):
        if len(self.searchVar.get()) == 0: 
            self.fill()
            return
        text = self.searchVar.get()
        self.fileList.delete(0, END)
        self.filtered = []
        for tab in self.list:
            if (self.match(text, tab[0]) > 0):
                self.filtered.append(tab)
                self.fileList.insert(END, tab[0])

    def match(self, text, name):
        #console.write('Look for ' + text + ' in ' + name)
        index = 0
        weight = 0
        found = 0
        last = -1
        size = len(text)
        uname = name.decode('utf-8')

        if len(text)==0:
            return 0
        for i in range(len(uname)):
            cc = uname[i]
            if cc == text[index]:
                weight = weight + 1 if i == last+1 else 1
                found += weight
                index += 1
                last = i
                if index == size: 
                    return found
        return 0
                        
TabSwitcher()

