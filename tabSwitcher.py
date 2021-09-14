from Tkinter import *
import tkFont
import ctypes
from ctypes import byref, Structure, wintypes
from ctypes.wintypes import BOOL, HWND, LPARAM, LONG

try:
    TabSwitcher().show()
except NameError:    
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

    class TabSwitcherFactory(type):
        _instance = None
        def __call__(cls, *args, **kwargs):
            if cls._instance is None:
                cls._instance = super(TabSwitcherFactory, cls).__call__(*args, **kwargs)
            return cls._instance

    class TabSwitcher():
        __metaclass__ = TabSwitcherFactory
        def __init__(self):

            # Styles
            self.windowStyle = {'background': 'black'}
            self.searchStyle = {'bg': 'black', 'fg': 'gray90', 'insertbackground': 'gray90', 'highlightcolor': 'PaleGreen3', 'highlightbackground': 'black', 'highlightthickness': 1, 'relief': 'flat'}
            self.listBoxStyle = {'activestyle': 'none', 'bg': 'gray8', 'fg': 'gray80', 'selectbackground': 'gray16', 'selectforeground': 'gray80',  'highlightthickness': 0}
            self.frameStyle = {'bg' : 'gray8'}

            # Search 
            self.lastSearch = ''

        def show(self):      
            self.root = Tk()

            # font
            self.font = tkFont.Font(root=self.root, family='Calibri', size=14)

            # Root
            self.center()

            self.root.configure(**self.windowStyle)
            self.root.attributes('-topmost',True)
            self.root.overrideredirect(1)
            self.root.wm_attributes('-alpha', 0.9)
            self.root.bind('<Escape>', self.quit)

            #Frame
            self.frame = Frame(self.root, **self.frameStyle)
            self.frame.pack(expand=True, fill=BOTH)

            # Search
            self.searchVar = StringVar()
            self.searchVar.set(self.lastSearch)
            self.searchVar.trace('w', self.filter)
            self.search = Entry(self.frame, textvariable = self.searchVar, font=self.font, **self.searchStyle)
            self.search.pack(expand=False, fill=X)
            self.search.bind('<Down>', self.down)
            self.search.bind('<Return>', self.first)

            self.filtered = []

            # List
            self.fileList = Listbox(self.frame, font= self.font, **self.listBoxStyle)
            self.list = list(map(self.tabWithShortName, notepad.getFiles()))
            self.fileList.bind('<Return>', self.go)
            self.fileList.pack(expand=True, fill=BOTH)
            
            self.filter()

            self.root.lift()
            self.root.focus_force()
            self.search.focus()

            last = len(self.searchVar.get())
            self.search.selection_range(0, last)
            self.search.icursor(last)

            self.root.mainloop()

        def tabWithShortName(self,tab):
            return tab + (self.shortname(tab[0]),)
        
        def shortname(self,name):
            return name if len(name) < 100 else '...' + name[-100:]

        def center(self):
            self.nppHwnd = ctypes.windll.user32.FindWindowW(u'Notepad++', None)
            if self.nppHwnd == 0: return
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(self.nppHwnd, byref(rect))
            w = rect.w * 0.75
            x = (rect.w - w)/2 + rect.x
            h = 400
            y = (rect.h - h)/2 + rect.y            
            geom = '%dx%d+%d+%d' % (w, h, x, y)
            self.root.geometry(geom)

        def down(self, event):
            size = self.fileList.size()
            pos = 1 if size > 1 else 0        
            self.fileList.select_clear(0, size-1)
            self.fileList.select_set(pos)
            self.fileList.activate(pos)
            self.fileList.focus()

        def first(self, event):
            self.fileList.select_set(0)
            self.go(event)

        def go(self, event):
            selected = self.fileList.curselection()
            if len(selected) == 0: return
            selIndex = selected[0]
            tab = self.list[selIndex] if len(self.filtered)==0 else self.filtered[selIndex]
            notepad.activateBufferID(tab[1])
            self.quit()
            
        def quit(self, *args):
            self.lastSearch = self.searchVar.get()
            self.root.destroy()
            
        def fill(self):
            self.fileList.delete(0,END)
            for tab in self.list: self.fileList.insert(END, tab[4])
        
        def filter(self, *args):
            if len(self.searchVar.get()) == 0: 
                self.fill()
                return
            text = self.searchVar.get()
            self.fileList.delete(0, END)
            self.filtered = []
            matched = []
            for tab in self.list:
                weight = self.match(text, tab[0])
                if (weight > 0):
                    matched.append((weight, tab))
            for m in sorted(matched, key=lambda item : item[0], reverse=True):
                self.filtered.append(m[1])
                self.fileList.insert(END, m[1][4])

        def match(self, text, name):
            size = len(text)
            start = 0
            end = 1
            uname = name.decode('utf-8').lower()
            if len(text)==0:
                return 0
            # start
            words = [0]
            wc = 0
            pos = 0
            last = 0

            while(end <= size):
                last = pos
                pos = uname.find(text[start:end].lower(), last)
                wlen = end - start
                if (pos >= 0):
                    words[wc] = wlen
                    end += 1
                else:
                    # single char not found - means no match
                    if (wlen==1): return 0
                    # otherwise reset search
                    pos = last + words[wc]
                    words.append(0)
                    wc += 1
                    start = end-1

            return sum(list(map(lambda x: sum(range(x+1)), words)))

                            
    TabSwitcher().show()

