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

    # def filter_hosts(self, line, group=None):
    #     return sum([line.find(x) for x in self.groups]) < 0 and line.strip()
    
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
        group = "[{}]".format(group.replace("[", "").replace("]", ""))

        if group == "[all]":
            return self.all

        if not group in self.groups:
            return []
        
        linenum = self.findline(group)
        if linenum is not None:
            hosts = []
            for i in self.readlines(linenum+1, -1):
                if i in self.groups: break
                hosts.append(Host(i))
            return hosts
        return []
    
    def findline(self, string):
        for i, line in enumerate(self.readlines()):
            if string == line:
                return i

    def read(self):
        return self.raw
    
    def readlines(self, count=None, end=None):
        output = self.raw.split("\n")

        if count and end:
            if end == -1:
                return output[count:]
            return output[count:count+end]
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