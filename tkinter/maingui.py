import os, sys                    
import json                                     # парсинг ответа ffprobe (входит в пакет ffmpeg)
import subprocess as sp                         # для запуска приложений командной строки
import threading                                

from datetime import datetime

from tkinter import *
from tkinter.ttk import *                       # override Button, Checkbutton, Entry, Frame, Label, LabelFrame, Menubutton, PanedWindow, Radiobutton, Scale and Scrollbar)
from tkinter.messagebox import askokcancel, showinfo
from tkinter.filedialog import askdirectory

from helpers.ffprogress import Transcoder               # управление ffmpeg
from helpers.dirbrowser import DirBrowserTree           # класс от ttk.Treeview с добавлением чекбокса и методов для дерева каталогов
from helpers.killthread import *                        # функция, убивающая поток из другого потока (штатных нет в python)

POSIX = 'posix' in sys.builtin_module_names     
WIDTH, HEIGHT = 640, 480                        # минимальные размеры окна приложения
DEBUG = False
TEST_CMD = 'ffmpeg -i "%s" -c:a ac3 -c:v h264 -y "%s"'


class Unbuffered():           # стаковерфлоу
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class MainWindow(Toplevel):
    def __init__(self, parent=None):
        self.parent = parent
        self.threads = []

        self.pipein, self.pipeout = os.pipe()
        self.stdout = sys.stdout
        sys.stdout = Unbuffered(os.fdopen(self.pipeout, 'w'))       # перехват stdout и направление без буферизации в пайп

        self.coder = Transcoder()
        self.working = False

        self._showHiddenInOpenDialogs()         # галка "скрытые файлы/папки"
        self.progress   = DoubleVar()           # or IntVar() StringVar()
        self.file_progress = DoubleVar()
        
        # стиль
        font       = ("Sans", 8, "normal")
        self.dirfont    = font[:-1] + ("bold",)
        self.style      = Style()
        self.style.configure('.', font=font)   # '.' == все ttk виждеты данного приложения

        # основные вкладки
        self.notebook   = Notebook(self.parent, width=WIDTH, height=HEIGHT)
        self.tab1       = self.makeMainFrame(self.notebook)         # фрейм выбора файлов
        self.tab2       = self.makeOptionsFrame(self.notebook)      # фрейм настроек
        self.tab3       = self.makeLogFrame(self.notebook)          # фрейм настроек
        self.tab4       = self.makeAboutFrame(self.notebook)        # фрейм настроек
        self.notebook.pack(side=TOP, fill=BOTH, expand=YES)
        self.notebook.add(self.tab1, text="Main")
        self.notebook.add(self.tab2, text="Options")
        self.notebook.add(self.tab3, text="Progress / Logging")
        self.notebook.add(self.tab4, text="About")
                        
        # строка статуса - самый низ
        self.bottom0        = Frame(relief=SUNKEN)
        self.statusBar      = Label(self.bottom0, text='...', relief=FLAT)
        self.sizegrip       = Sizegrip(self.bottom0)
        self.progressBar    = Progressbar(self.bottom0, length=100, mode='determinate', variable=self.progress)
        self.bottom0.pack(side=BOTTOM, expand=NO, fill=X)
        self.statusBar.pack(side=LEFT, fill=X, expand=YES)
        self.sizegrip.pack(side=RIGHT, expand=NO)
        self.progressBar.pack(side=LEFT, expand=NO)

        # второй низ окна - с кнопками
        self.bottom1        = Frame()
        self.ConvertButton  = Button(self.bottom1, text='Convert', command=self.onConvert)
        self.PanicButton    = Button(self.bottom1, text='Panic', command=self.onPanic)
        self.QButton        = Button(self.bottom1, text='Quit', command=self.onQuit)
        self.bottom1.pack(side=BOTTOM, expand=NO, fill=X, anchor=S)
        self.ConvertButton.pack(side=LEFT)
        self.PanicButton.pack(side=LEFT)
        self.QButton.pack(side=LEFT)
                
        # установить минимальные размеры окна
        self.parent.update_idletasks()
        self.parent.after_idle(lambda: self.parent.minsize(self.parent.winfo_width(), self.parent.winfo_height()))

        if not DEBUG: self.parent.protocol("WM_DELETE_WINDOW", self.onQuit)     # set cmd on x-button
        if DEBUG: self._addFolderToTree()

    # формирование окна выбора файлов
    def makeMainFrame(self, parent=None):
        mf = Frame(parent)
        top = Frame(mf)
        top.pack(expand=NO, fill=X, anchor=N)
                
        # кнопка выбора рабочей директории
        addBtn      = Button(top, text='Add', command=self.addDir)
        remBtn      = Button(top, text='unAdd', command=self.unaddDir)
        addBtn.pack(side=LEFT)
        remBtn.pack(side=LEFT)

        # две панели (список файлов, информация)
        self.pw         = PanedWindow(mf, orient=HORIZONTAL)        # зогадко: self.pw.__module__ == tkinter.ttk, а опции ttk недоступны
        self.filesPan   = LabelFrame(text='Files', labelanchor=NW)
        self.infoPan    = LabelFrame(text='Info', labelanchor=NW)
        self.pw.add(self.filesPan)
        self.pw.pack(fill=BOTH, expand=YES)
        self.pw.add(self.infoPan)

        self.parent.after(200, self.pw.sashpos, *(0, WIDTH//2))     # выставить разделитель на середину, почему-то только так 
                                                                    # (Ubuntu поначалу было достаточно 0 паузы, Win - ~100), и sash_place не работает

        # дерево файлов (на старте тут опции дерева и заглушка)
        self.TreeOptions    = dict(columns          = ("fullpath", "type", "size", "Size"),
                                   displaycolumns   = ("Size",),
                                   selectmode       = "extended",   # browse - The user may select only one item at a datetime.   
                                                                    # extended - The user may select multiple items at once.
                                   dirfont          = self.dirfont)

        self.fileTree       = DirBrowserTree(self.filesPan, startpath=None, progressVar=self.progress, **self.TreeOptions) 
        self.fileTree.treeview.pack(fill=BOTH, expand=YES)  # показать
        self.fileTree.treeview.bind("<<TreeviewSelect>>", self.onSelect) # обработчик выбора, или <Double-1> - двойной
        self.fileTree.treeview.bind("<Button-3>", self.onEmptyRightClick)          # обработчик выбора, или <Double-1> - двойной

        # информация о файле
        text = Text(self.infoPan, font=("Mono", 8, "normal"), relief=SUNKEN, bg=parent.master.cget("bg"))
        text.config(wrap=NONE)                                      # не переносить длинные строки
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        text.tag_config("header", font=("Mono", 9, "bold"), justify=CENTER) # тэг для заголовков
        if POSIX: text.bind("<Button>", lambda event: text.focus_set())     # to enable copy from disabled widget (on Win is not necessary)
        
        self.fileInfo = text
        return mf

    def makeOptionsFrame(self, parent=None):
        of = Frame(parent)
        of.pack(expand=NO, fill=X, anchor=N)

        Label(of, text="Command:", font=self.dirfont).pack(side=TOP, anchor=NW)
        self.cmd = Entry(of, takefocus=0)
        self.cmd.insert(0, TEST_CMD)
        self.cmd.pack(anchor=N, fill=X, expand=YES)

        cb_names = {'Verbose logging': 0, 'Remove original after transcode': 0, 'Remove transcoded (no need except debugging)': 1 if DEBUG else 0}
        self.cbs = {}
        for cb, val in cb_names.items():
            var = IntVar()
            var.set(val)
            self.cbs[cb] = (Checkbutton(of, text=cb, variable=var), var)
            self.cbs[cb][0].pack(side=LEFT)
        
        return of

    def makeLogFrame(self, parent=None):
        lf = Frame(parent)
        lf.pack(expand=NO, fill=X, anchor=N)

        pp = LabelFrame(lf, text='Progress', labelanchor=NW)
        pp.pack(fill=BOTH, expand=NO)
        lp = LabelFrame(lf, text='Log', labelanchor=NW)
        lp.pack(fill=BOTH, expand=YES)
        
        self._curr_file = Label(pp, text='Current file: ...')
        self._curr_file.pack(side=TOP, fill=BOTH, expand=YES)
        self._file_prog = Progressbar(pp, length=100, mode='determinate', variable=self.file_progress)
        self._file_prog.pack(side=TOP, fill=BOTH, expand=YES)
        self._elapsed = Label(pp, text='...', font=("Mono", 8, "bold"))
        self._elapsed.pack(side=TOP, fill=BOTH, expand=YES)
        self._estimated = Label(pp, text='...', font=("Mono", 8, "bold"))
        self._estimated.pack(side=TOP, fill=X, expand=YES)
        self._state = Label(pp, text='...\n'*4, font=("Mono", 8, "normal"))
        self._state.pack(side=TOP, anchor=N, fill=X, expand=YES)
        
        sbar = Scrollbar(lp)
        self._log = Text(lp, font=("Mono", 8, "normal"))
        # self._log.config(state=DISABLED)
        sbar.config(command=self._log.yview)         # связать sbar и text
        self._log.config(yscrollcommand=sbar.set)    # сдвиг одного = сдвиг другого
        sbar.pack(side=RIGHT, fill=Y)           # первым добавлен - посл. обрезан
        self._log.pack(side=TOP, expand=YES, fill=BOTH)
        # if POSIX: self._log.bind("<Button>", lambda event: self._log.focus_set())     # to enable copy from disabled widget (on Win is not necessary)

        self._logger('Start logging\n')
        self._stoplogging = False
        t = threading.Thread(target=self._startLogger, args=(self._logger, self._stoplogging))
        t.setDaemon(True)       # byf
        t.start()

        return lf

    def makeAboutFrame(self, parent=None):
        af = Frame(parent)
        af.pack(expand=NO, fill=X, anchor=N)
        Label(af, text="\nSimple GUI for FFmpeg\nv0.1\n\n2020", justify=CENTER).pack(side=TOP)
        
        return af

    def _showHiddenInOpenDialogs(self):
        """ StackOverflow tcl/tk hack (на askdirectory тоже действует)
        """
        if POSIX:                                       # в виндоуз не работает в принципe
            try: 
                self.parent.tk.call('tk_getOpenFile', '-abrakadabra')               # вызвать (с ошибкой, чтоб не отрисовалось)
            except TclError: pass
            self.parent.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')    # добавить чекбокс про скрытые файлы
            self.parent.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')    # не чекать его

    def _get_options(self):
        options = {}
        for cb, val in self.cbs.items():
            options[cb.lower()] = val[1].get()
        return options

    def _get_command(self):
        return self.cmd.get()    # Returns the entry's _cur_file text as a string.

    def _get_tasks(self):
        files = []
        sizes = []
        for item in self.fileTree.treeview.tagged(in_tags=("checked", ), ex_tags=("dir", )):
            if 'file' in item['values']:
                fullpath =  item['values'][0]
                size = item['values'][2]
                files.append(fullpath)
                sizes.append(size)
        return files, sizes

    def _update_file_info(self, msg, *options):
        self.fileInfo.configure(state=NORMAL)
        self.fileInfo.delete('1.0', END)                                    # удалить текущий текст
        self.fileInfo.insert(END, msg if msg else '', options)
        self.fileInfo.update()
        self.fileInfo.configure(state=DISABLED)

    def _report_file(self, report):
        try:
            report['format']
        except KeyError:
            self._update_file_info('unknown file format', "header")
        else:
            self.fileInfo.configure(state=NORMAL)
            self.fileInfo.delete('1.0', END)                                # удалить текущий текст
            self.fileInfo.insert(END, 'File format:\n', "header")           # тэг заголовка
            for k,v in report['format'].items():
                if type(v) in (type({}), type([])):
                    v = "...see ffprobe output for full info"               # skip embedded dicts
                kv = "{:>20} : {}\n".format(str(k), str(v))                 # format section
                self.fileInfo.insert(END, kv)
            self.fileInfo.insert(END, '\nStreams:', ("header",))         
            for stream in report['streams']:                
                self.fileInfo.insert(END, '\n')
                for k,v in stream.items():  
                    if type(v) in (type({}), type([])):
                        v = "...see ffprobe output for full info"
                    kv = "{:>20} : {}\n".format(str(k), str(v))             #  streams section
                    self.fileInfo.insert(END, kv)

            self.fileInfo.update()                                          # redraw
            self.fileInfo.configure(state=DISABLED)                         # readonly (disables copy/paste too)

    def _check_format(self, filename):
        cmd =  ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filename)
        try:
            text = sp.check_output(cmd)
        except sp.CalledProcessError: # unknown file format
            return -1
        return 0

    def _update_selection(self):
        files = size = 0
        self.statusBar.config(text='Counting files...')
        for item in self.fileTree.treeview.tagged(in_tags=("checked", ), ex_tags=("dir", "broken")):            
            files += 1
            size += item['values'][2]
        rsize = self.fileTree._readable_size(size)
        text = 'Selected: {} files ({})'.format(files, rsize) if files > 0 else '...'
        self.statusBar.config(text=text)
    
    def _addFolderToTree(self):
        """ добавить в treeview """
        idir = '/mnt/EXT_STORAGE/Movies/1_testdir' if DEBUG else ('/' if POSIX else 'С:\\')
        newdir = askdirectory(initialdir=idir)    
        self.statusBar.config(text="Scanning folders...")
        if newdir:
            try:
                self.fileTree.new_root(self.fileTree.treeview, newdir)  # добавить папку
            except Exception:                                           # не получилось (PermissionError или др.)
                import traceback
                print('[Error adding new dir to tree:]', sys.exc_info()[1])
        else:
            pass
        self.statusBar.config(text="...")
        self.progress.set(0)

    def _encodingProgress(self, started, ifile, state, total_frames):
        i = self.files.index(ifile)
        l = len(self.files)
        if state != 'break':
            file_progress = round(int(state['frame']) / total_frames * 100)
            total_progress = (sum(self.sizes[:i]) + round(self.sizes[i] * file_progress / 100) ) / sum(self.sizes)
            total_progress = total_progress * 100
            # if l == 1: total_progress = file_progress
            text = 'Total progress: {:0.1f} %'.format(total_progress)
            
            curr = 'Current file: {} [ {}/{} ]'.format(ifile, i+1, l)
            self._curr_file.config(text=curr)
            self.file_progress.set(file_progress)

            _el = datetime.now() - started
            _elt = datetime.now() - self._started
            
            _els = "{:>10}: {} total ({} current file)".format('Elapsed', str(_elt).split('.')[0], str(_el).split('.')[0])
            self._elapsed.config(text=_els)
            _es = _el * (101 / (file_progress + 1) ) - _el
            _est = _elt * (101 / (total_progress + 1) ) - _elt
            _ess = "{:>10}: {} total ({} current file)".format('Estimated', str(_est).split('.')[0], str(_es).split('.')[0])
            self._estimated.config(text=_ess)
            
            _st = ''
            for s, v in state.items():
                if s in ['frame', 'fps', 'bitrate', 'speed']:
                    _st += '{:>10}: {}\n'.format(s,v)
            self._state.config(text=_st)

            if total_progress >= 100:
                self.statusBar.config(text='Done!')
            else:
                self.statusBar.config(text=text)
            
            self.progress.set(total_progress)
        else:
            self.statusBar.config(text='Canceled!')

    def _decodeChecked(self):
        command = self._get_command()
        self.files, self.sizes = self._get_tasks()
        self.coder.config(**self._get_options())
        
        self._started = datetime.now()
        for file in self.files:
            self.coder.start(file, command, self._encodingProgress)
        
        self.working = False

    def _logger(self, msg):
        t = str(datetime.now()).split('.')[0]
        logMsg = '<{}> {}'.format(t, msg)
        self._log.configure(state=NORMAL)
        self._log.insert(END, logMsg)
        self._log.update()
        self._log.configure(state=DISABLED)
    
    def _startLogger(self, callback, stop):
        chunk = ''
        while True:
            chunk += os.read(self.pipein, 256).decode(errors='ignore')     # 256 достаточно, чтоб получить строку прогресса целиком 
            if chunk.endswith('\n'):
                self.stdout.write(chunk)
                self.stdout.flush()
                callback(chunk)
                chunk = ''
    
    # commands
    def addDir(self):
        t = threading.Thread(target=self._addFolderToTree)
        self.threads.append(t)
        t.start()

    def unaddDir(self):
        iids = self.fileTree.treeview.selection()       # выделенный узел
        remove = self.fileTree.remove_node              # метод удаления
        exists = self.fileTree.treeview.exists          # метод проверки существования
        [remove(i) for i in iids if exists(i)]          # вжжик
        self._update_selection()

    def onSelect(self, event):
        self.progress.set(0)

        iid = self.fileTree.treeview.focus()
        item = self.fileTree.treeview.item(iid)
        if DEBUG: print('focus on:', item['values'])
        if iid: # skip 'ghost' selections after deleting items
            if item['values'][1] == 'file':
                filename = item['values'][0]
                cmd =  ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filename)
                try:
                    text = sp.check_output(cmd, encoding=sys.getdefaultencoding())
                except FileNotFoundError as e: # no ffprobe
                    self._update_file_info(r'...go to https://ffmpeg.org/ to install ffmpeg tools...', "header")
                except sp.CalledProcessError as e:  # ffprobe error
                    self._update_file_info(r'...unrecognized file format...', "header")
                    self.fileTree.treeview.set_tag(iid, "broken")
                else:
                    report = json.loads(text)
                    self._report_file(report)
            elif 'directory' in item['values']:
                self._update_file_info('...directory...', "header")
            
            t = threading.Thread(target=self._update_selection)
            self.threads.append(t)
            t.start()
    
    def onEmptyRightClick(self, event):
        "If empty tree -> add dir on right click"
        if len(self.fileTree.treeview.get_children()) == 0:
            self.addDir()

    def onConvert(self):
        if not self.working:
            self.working = True
            t = threading.Thread(target=self._decodeChecked)
            self.threads.append(t)
            t.start()
        else:
            showinfo("Work in progress!", "Press 'Panic' to cancel")

    def onPanic(self):
        self.working = False
        self.progress.set(0)
        self.coder.kill_n_clear()
        # if DEBUG: print('list of threads:', self.threads)

        for t in self.threads:
            try:
                res = terminate(t)
                self.threads.remove(t)
                if res == 1:
                    print('[terminated] {} (code: {})'.format(t, res))
                elif res == -1:
                    print('[removed dead] {} (code: {})'.format(t, res))
            except WrongThreadID:   # res == 0
                self.threads.remove(t)
                print('[WrongThreadID] {} (code: {})'.format(t, res))
        
        print('Active threads:', threading.activeCount())

    def onQuit(self):
        if askokcancel('Verify exit', "Really quit?"): 
            self.coder.kill_n_clear()
            self.parent.quit()
            self._stoplogging = True


if __name__ == '__main__':
    # test
    root = Tk()
    root.title('Simple GUI for ffmpeg')
    win = MainWindow(root)
    # win.parent.title('Test window')
    mainloop()