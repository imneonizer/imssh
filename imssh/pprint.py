    def clean(self, line):
        # clean string to remove any kind of shell color formatting
        return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).replace('\b', '').replace('\r', '')

    def get_color_escape(self, r, g, b, background=False):
        return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)
    
    def colorize(self, string):
        RESET = '\033[0m'
        return self.get_color_escape(*self.get_rgb(self.host))+string+RESET

    def get_rgb(self, string):
        if "." in string:
            string = string.split(".")[-1]
        h = str(int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16) % 10**9)
        r, g, b = int(h[:3]), int(h[3:6]), int(h[6:])
        s, scale = r + g +b, 255
        r, g, b = round((r/s)*scale), round((g/s)*scale), round((b/s)*scale)

        h = int(hashlib.md5(string.encode('utf-8')).hexdigest(), 32) % 10**1
        h = round(h / 3)

        if h == 0:
            r = r**10
        elif h == 1:
            g = g**10
        else:
            b = b**10
        
        return r, g, b
    
    def pprint(self, string, pattern=0, end=None):
        try:
            pattern = self.pattern[pattern]
        except:
            pattern = self.pattern[0]

        pprint_lock.acquire()
        try:
            for line in string.split("\n"):
                print(self.colorize(pattern), "|", line)
            if end:
                print(end, end='')
        except Exception:
            raise
        finally:
            pprint_lock.release()
