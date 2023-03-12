"""Перекодирование видеофайлов в папках в формат, совместимый с плеером PS4"""
import sys, os
import subprocess
import _thread
import json
from datetime import datetime

DEBUG = False

REMOVE_INPUT_FILES = True
REMOVE_OUTPUT_FILES = True if DEBUG else False

CPU   = 'ffmpeg -i "%s" -c:a ac3 -c:v h264 -y "%s"'                                   # самый надежный вариант (и похоже h264 автоматом заменяется h264_nvenc)
CPUm  = 'ffmpeg -i "%s" -map 0 -c:a ac3 -c:v h264 -y "%s"'                            # через map
GPU0  = 'ffmpeg -vsync 0 -i "%s" -map 0 -c:a ac3 -c:v h264_nvenc -b:v 3M -y "%s"'     # используя GPU (надо компилить ffmpeg с поддержкой GPU)
GPU1  = 'ffmpeg -hwaccel cuda -i "%s" -c:v h264_nvenc -preset hq -y "%s"'
GPU2  = 'ffmpeg -i "%s" -c:v h264_nvenc -profile:v high -pixel_format yuv444p -preset 10 "%s"'
AC3   = 'ffmpeg -i "%s" -c:a ac3 -c:v copy -y "%s"'                                   # декодировать только аудио в AC3

cmd = CPUm

def parse_state(s):
    L = [item for sublist in s.split('=') for item in sublist.strip().split()]      # неочевидно, хоть и правильно

    names = L[0::2]     # нечетные - имена
    vals = L[1::2]      # четные - значения
    state_dict = dict(zip(names, vals))
    return state_dict

def readState(pipe, fr_total, callback=None):
    while True:
        output = os.read(pipe, 256).decode()        # 256 достаточно, чтоб получить строку прогресса целиком 
        output = output.split('\n')
        for s in output:
            if s.startswith('frame='):              # найти в выводе строку прогресса
                d = parse_state(s)                  # распарсить в словарь
                callback(d, fr_total)               # вызвать обработчик

def getTotal(inputfile):
    cmd =  ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', inputfile)
    try:
        text = subprocess.check_output(cmd, encoding=sys.getdefaultencoding())
    except subprocess.CalledProcessError: # unknown file format
        return -1
    probe = json.loads(text)
    dur = float(probe['format']['duration'])
    fps = probe['streams'][0]['avg_frame_rate'].split('/')
    fps = int(fps[0])/int(fps[1])
    # fps = float(eval(probe['streams'][0]['avg_frame_rate']))
    nb_frames = int(dur * fps)
    return nb_frames

def reportProgress(d, total):
    l = 40
    progress = int(d['frame']) / total
    to_fill = round(progress*l)
    bar = '░' * to_fill + '.' * (l - to_fill)

    print('\r-> [{}] {:3.0f}%'.format(bar, progress*100), end=' ')

def decodeFile(inputfile, remove=False, clear=False):
    pipein, pipeout = os.pipe()                                 # получить дескрипторы нового пайпа

    print('Current file:', inputfile, end='\n')
    outputfile = inputfile[:-3] + 'H264.mp4'
       
    coded = False
    if not os.path.isfile(outputfile):                                    # если еще не перекодировали
        if DEBUG: print('-> CLI command:', cmd % (inputfile, outputfile))
        p = subprocess.Popen(cmd % (inputfile, outputfile), 
                             stdout=pipeout, stderr=pipeout, shell=True)  # ffmpeg пишет в stderr(!)
        total = getTotal(inputfile)                                       # получить длину файла в фремах
        t = _thread.start_new_thread(readState, (pipein, total, reportProgress,))  # запустить чтение вывода ffmpeg в отдельном процессе

        if p.wait() == 0:   # p.wait() блокирует основной процесс до окончания Popen
            coded = True                          
            print('Done!')
        else:
            print('-> Failed to transcode!')
    else:    
        print('-> Skip: allready transcoded!')
    
    if coded and remove:
        os.popen('rm "%s"' % inputfile)            # удалить исходные файлы
        print('-> Removed: ', inputfile)
    
    if coded and clear:
        os.popen('rm "%s"' % outputfile)           # удалить выходные файлы (для тестирования)
        print('-> Cleared: ', outputfile)
    
    print()

def decodeFolder(path, remove=True, clear=False):
    tree = os.walk(path)
    for folder in tree:
        folder_name, files = folder[0], folder[-1]
        print(folder_name)
        for file in [f for f in files if f[-8:] != 'H264.mp4']:              # skip allready transcoded
            inputfile = folder_name + '/' + file
            decodeFile(inputfile, remove=remove, clear=clear)


if __name__ == '__main__':

    root = "/mnt/EXT_STORAGE/Movies/"
    toDecode = [root + "The IT Crowd",
               ]

    start_time = datetime.now()
    for item in toDecode:
        if os.path.isfile(item):
            decodeFile(item, remove=REMOVE_INPUT_FILES, clear=REMOVE_OUTPUT_FILES)
        elif os.path.isdir(item):
            decodeFolder(item, remove=REMOVE_INPUT_FILES, clear=REMOVE_OUTPUT_FILES)
        else:
            print("Wrong path to input:", item)
    
    elapsed = (datetime.now() - start_time)
    print('Elapsed (hh:mm:ss): {}'.format(str(elapsed).split('.')[0]))