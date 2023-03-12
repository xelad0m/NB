
import ctypes

class WrongThreadID(Exception):
    pass

def terminate(thread):
    """Terminates a python thread (both daemoned 
    or not)  from another thread.
    :param thread: a threading.Thread instance
    """
    if hasattr(thread, 'ident'):    # instance given
        tid = thread.ident      
        if not thread.is_alive():   # allready dead
            return -1
    else:                           # thread id given
        tid = thread

    exc = ctypes.py_object(SystemExit)  # class SystemExit -> C object
    # then call C func from PyDLL. Returns the number of thread states modified
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), exc)

    if res == 0:
        raise WrongThreadID("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble (no),
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    return res

if __name__ == '__main__':
    # testы
    import threading, _thread
    import time

    def do_work():
        i = 0
        while True:
            print(i)
            i += 1
            time.sleep(0.5)
    
    # threading
    t = threading.Thread(target=do_work)
    # t.daemon = True  # works too
    t.start()
    print(threading._active.items())
    time.sleep(1)
    print("is_alive?", t.is_alive())
    print('terminating')
    terminate_thread(t)
    time.sleep(1)
    print("is_alive?", t.is_alive())
    terminate_thread(t)     # returns None cos threading.Thread() can check if its alive


    # _thread
    tid = _thread.start_new_thread(do_work, ())
    print(tid in threading._active.items())  # False
    time.sleep(1)
    time.sleep(1.1)
    terminate_thread(tid)

    print(threading._active)
    tid = _thread.start_new_thread(print, ('tiny thread',))
    try:
        terminate_thread(tid)
    except WrongThreadID as e:
        print("Caught  exception:", e)

    # sleeping thread
    tid = _thread.start_new_thread(time.sleep, (10,))
    t = threading.Thread(target=(lambda: time.sleep(10)))
    time.sleep(1)
    terminate_thread(t)
    print('sleep terminated')   # спящий поток тоже прерывается, а писали не прокатит