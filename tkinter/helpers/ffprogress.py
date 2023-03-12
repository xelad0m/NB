"""
inspired by https://github.com/Tatsh/ffmpeg-progress
"""

from datetime import datetime
import json
import os, sys
import subprocess, threading

from . import killthread

POSIX = 'posix' in sys.builtin_module_names

REMOVE_CMD  = 'rm "%s"' if POSIX else 'del "%s"'
PROBE_CMD   = ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams')

STOP = "StOp"   # ¯\_(ツ)_/¯
FINISH = "FiNiSh"

class Transcoder():
    def __init__(self, trace=False, remove=False, clear=False):
        self.trace = trace
        self.remove = remove
        self.clear = clear

        self.popens = []
        self.threads = []
        self.tempfiles = []

        self.pipein, self.pipeout = os.pipe()                                          # получить дескрипторы нового пайпа
    

    def _parse_state(self, raw):
        L = [item for chunck in raw.split('=') for item in chunck.strip().split(' ')]  # нарезать строку состояния по пробелами и '='
        names = L[0::2]     # нечетные - имена
        vals = L[1::2]      # четные - значения
        state_dict = dict(zip(names, vals))
        return state_dict

    def _nb_frames(self, probe):
        fps = None
        for stream in probe['streams']:
            if stream['codec_type'] == 'video':
                dur = float(probe['format']['duration'])
                fps = stream['avg_frame_rate'].split('/')
                try:
                    fps = int(fps[0])/int(fps[1])
                except ZeroDivisionError:
                    fps = 0
                nb_frames = int(dur * fps)
                return nb_frames                        # 1st video stream in file
        if not fps:
            return 0                                    # no video stream in file

    def _startStateReader(self, now, inputfile, total_frames, callback=None):
        while True:
            output = os.read(self.pipein, 256).decode(errors='ignore')     # 256 достаточно, чтоб получить строку прогресса целиком 
            output = output.split('\n')
            for s in output:
                if s.startswith('frame='):                          # найти в выводе строку прогресса
                    state = self._parse_state(s)                    # распарсить в словарь
                    callback(now, inputfile, state, total_frames)   # вызвать обработчик
            if STOP in output:  
                callback(now, inputfile, 'break', total_frames)                              
                break                                               
            if FINISH in output:
                break
    
    def _stopStateReader(self, msg):
        os.write(self.pipeout, msg.encode())

    def config(self, **options):
        for key, val in options.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def probe(self, inputfile):
        try:
            text = subprocess.check_output(PROBE_CMD + (inputfile,), encoding=sys.getdefaultencoding())
        except subprocess.CalledProcessError:          
            return False                                # unknown file format
        else:
            probe = json.loads(text)
            return probe

    def transcode(self, inputfile, command, total_frames, onProgressCallback):
        outputfile = inputfile[:-3] + 'H264.mp4'
        self.tempfiles.append(outputfile)
        
        coded = False
        if not os.path.exists(outputfile):                                  # если еще не перекодировали
            # print(command % (inputfile, outputfile))
            p = subprocess.Popen(command % (inputfile, outputfile), 
                                stdout=self.pipeout, stderr=self.pipeout,   # ffmpeg пишет в stderr(!)
                                shell=True, start_new_session=True)         # без start_new_session не получится кильнуть пул процессов ffmpeg
            self.popens.append(p)
            
            t = threading.Thread(target=self._startStateReader,             # запустить чтение вывода ffmpeg в отдельном процессе
                                args=(datetime.now(), inputfile, total_frames, onProgressCallback))
            self.threads.append(t)
            t.start()

            if p.wait() == 0:                               # p.wait() блокирует родительский процесс до окончания Popen
                coded = True
                self.popens.remove(p)
                self._stopStateReader(FINISH)
                self.threads = []                           # неубитые потоки - сами по себе
                self.tempfiles.remove(outputfile)
                if self.trace: print('Done!')
        else:    
            if self.trace: print('-> Skip: allready transcoded!')

        if coded and self.remove:
            os.popen(REMOVE_CMD % inputfile)                # удалить исходные файлы
            if self.trace: print('-> Removed: ', inputfile)
        
        if coded and self.clear:
            os.popen(REMOVE_CMD % outputfile)               # удалить выходные файлы (для тестирования)
            if self.trace: print('-> Cleared: ', outputfile)

    def start(self, inputfile, command, onProgressCallback):
        probe = self.probe(inputfile)
        if probe:
            total = self._nb_frames(probe)                  # получить длину файла в фремах

            if total != 0:
                if self.trace: print("started transcoding: %s" % inputfile)
                t = threading.Thread(target=self.transcode, 
                                    args=(inputfile, command, total, onProgressCallback))
                self.threads.append(t)
                t.start()
                if __name__ != "__main__": t.join()         # не стартовать следующий, пока предыдущий не закончился
            else:
                if self.trace: print('[Err] No video stream in current file')

    def kill_n_clear(self):
        self._stopStateReader(STOP)
        if self.popens or self.threads or self.tempfiles:
            try:
                for p in self.popens:
                    import signal
                    os.killpg(p.pid, signal.SIGTERM)        # ffmpeg порождает группу процессов, поэтому только так
                    self.popens.remove(p)
                for t in self.threads:
                    killthread.terminate(t)
                    self.threads.remove(t)
                for f in self.tempfiles:
                    if os.path.exists(f): 
                        print(f, os.path.exists(f))
                        os.popen(REMOVE_CMD % f)
                    self.tempfiles.remove(f)
            except:
                if self.trace: print(sys.exc_info()[1])
            else:
                if self.trace: print("[msg] Transcoding canceled!")
        else:
            if self.trace: print("[msg] Nothing to cancel!")

def defaultReport(now, infile, state, total):
    l = 40
    if state != 'break':
        progress = int(state['frame']) / total
        to_fill = round(progress*l)
        bar = '░' * to_fill + '.' * (l - to_fill)
        print('\r-> [{}] {:3.0f}%'.format(bar, progress*100), end=' ')

if __name__ == "__main__":
    # test
    file = "/mnt/EXT_STORAGE/Movies/1_testdir/C.mkv" #A.mp4"
    command = 'ffmpeg -i "%s" -c:a ac3 -c:v h264 -y "%s"'

    print(file)
    coder = Transcoder(trace=True, remove=False, clear=True)
    coder.start(file, command, defaultReport)
    import time
    time.sleep(5)
    coder.kill_n_clear()