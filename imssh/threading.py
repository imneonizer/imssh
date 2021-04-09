import threading
import concurrent.futures

sync_lock = threading.Lock()

class Thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        threading.Thread.join(self)
        return self._return

class ConcurrentThreadPool:
    def map(self, target, args):
        result = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(target, arg) for arg in args]
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())

        return result

class ThreadPool:
    def map(self, target, args):
        threads = [Thread(target=target, args=(arg,)) for arg in args]
        [t.start() for t in threads]
        return [t.join() for t in threads if t.join()]

def map(target, args, concurrent=False):
    if concurrent:
        return ConcurrentThreadPool().map(target=target, args=args)
    return ThreadPool().map(target=target, args=args)

def sync(func):
    def inner(*args, **kwargs):
        sync_lock.acquire()

        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            sync_lock.release()

    return inner