import collections

class History:
    def __init__(self, stdin_maxlen, stdout_maxlen):
        self._stdin = collections.deque(maxlen=stdin_maxlen)
        self._stdout = collections.deque(maxlen=stdout_maxlen)
    
    @property
    def stdin(self):
        return self._stdin
    
    @property
    def stdout(self):
        return self._stdout