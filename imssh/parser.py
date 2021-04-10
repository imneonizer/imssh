import re

class Host(str):
    def __init__(self, raw):
        self.raw = raw.strip()
        self.username = self.extract_username()
        self.host = self.extract_host()
        self.port = self.extract_port()
        self.password= self.extract_password()
        self.sshkey = self.extract_sshkey()

    def extract_host(self):
        def isolate(ret):
            ret = ret.strip()
            if ":" in ret:
                ret = ret.split(":")[0]
            elif "!" in ret:
                ret = ret.split("!")[0]
            elif " " in ret:
                ret = ret.split(" ")[0]
            else:
                ret = ""
            return ret.strip()

        if "@" in self.raw:
            ret = self.raw.split("@")[1]
            return isolate(ret)
        else:
            return isolate(self.raw) or self.raw
    
    def extract_username(self):
        if "@" in self.raw:
            return self.raw.split("@")[0].strip()
    
    def extract_port(self):
        if ":" in self.raw:
            ret = self.raw.split(":")[1]
            ret = re.findall(r"\d+", ret)
            if ret:
                return int(ret[0])
        return 22
    
    def extract_password(self):
        if " " in self.raw:
            return self.raw.split(" ")[-1].strip()
    
    def extract_sshkey(self):
        if "!" in self.raw:
            ret = self.raw.split("!")[1]
            if " " in ret:
                return ret.split(" ")[0].strip()
            return ret.strip()

    def __repr__(self):
        return repr(self.__dict__)
    
    def __str__(self):
        return self.__repr__()
    
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]


class DataLoader:
    def __init__(self, path):
        self.path = path
        self.group_re = re.compile(r"\[.*\]", re.MULTILINE)
        self.groups = []
        self.all = []

        with open(path, "r") as f:
            self.raw = '\n'.join([x.strip() for x in f.read().strip().split("\n") if self.filter_comment(x)])
            self.groups = re.findall(self.group_re, self.raw)
            if self.groups:
                self.all = [Host(x) for x in self.raw.split("\n") if x not in self.groups]

        self.cache = {}
    
    def filter_hosts(self, line, group=None):
        return sum([line.find(x) for x in self.groups]) < 0 and line.strip()
    
    def filter_comment(self, line):
        line = line.strip()
        if not line:
            return False
        elif line.startswith("#"):
            return False
        elif line.startswith(";"):
            return False
        return True

    def get(self, group):
        if group == "all" or group == "[all]":
            return self.all
        else:
            group = group.strip().lstrip("[").rstrip("]")

            if group in self.cache:
                return self.cache[group]

            if "[{}]".format(group) not in self.groups:
                return None
            
            try:
                raw = self.raw[self.raw.find(group):].split("\n", 1)[1]
                ending_group = re.findall(self.group_re, self.raw)

                if ending_group:
                    raw = raw.split(ending_group[0])[0]
                    raw = [Host(x.strip()) for x in raw.split("\n") if self.filter_comment(x)]

                    self.cache[group] = raw
                    return raw
            except IndexError:
                return

    def read(self):
        return self.raw
    
    def readlines(self, count=None):
        output = self.raw.split("\n")
        if count:
            return output[:count]
        return  output

    def asdict(self):
        return {group.lstrip("[").rstrip("]"):self.get(group) for group in self.groups}
    
    def __iter__(self):
        return iter(self.asdict().items())

    def __repr__(self):
        return str(self.asdict())
    
    def __str__(self):
        return self.__repr__()
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self