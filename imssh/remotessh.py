import re
import os
import time
import getpass
import paramiko

from .sftp import Sftp
from .history import History
from .pprint  import PPrint
from .scripts import Scripts

class RemoteSSH(Sftp, PPrint, Scripts):
    def __init__(self, *args, **kwargs):
        if args or kwargs:
            self.connect(*args, **kwargs)

    def connect(self, username, host, password, \
                 host_keys="/dev/null", port=22, timeout=5, \
                 stdin_history_size=10, stdout_history_size=20):

        self.localusername = getpass.getuser()
        self.username = username.strip()
        self.host = host.strip()
        self.hostname = host
        self.password = password
        self.host_keys = host_keys
        self.port = port
        self.timeout = timeout
        self.stdin_history_size = stdin_history_size
        self.stdout_history_size = stdout_history_size
        self.init_session()

        self.pattern = [
            self.host,
            self.host,
            self.hostname,
            "{}@{}".format(self.username, self.host),
            "{}@{}".format(self.username, self.hostname),
            "{}@{} => {}".format(self.username, self.hostname, self.host),
        ]

        return self
    
    def init_session(self):
        self.session = paramiko.SSHClient()
        self.session.load_host_keys(self.host_keys)
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.session.connect(
            username=self.username,
            hostname=self.host,
            password=self.password,
            port=self.port,
            timeout=self.timeout
        )

        self.channel = self.session.invoke_shell()
        self.stdin = self.channel.makefile('wb')
        self.stdout = self.channel.makefile('r')
        self.sftp = self.session.open_sftp()

        self.history = History(
            self.stdin_history_size,
            self.stdout_history_size
        )

        self.hostname = self.execute("hostname").strip()

    def __del__(self):
        try:
            self.sftp.close()
            self.session.close()
        except: pass

    def reset(self):
        self.session.close()
        self.init_session()

    def interrupt(self):
        # sends program terminate command, i.e, ctrl+c
        self.stdin.write("\x03")
    
    def write_password(self, password=None):
        # write password to the shell
        self.stdin.write(password or self.password + "\n")
    
    def execute(self, command, pprint=0, end='', sudo=False):
        # execute a single command and return output without writing to stdin
        # faster than stdin.write
        if command.startswith("sudo") or sudo:
            command = "echo {} | sudo -S {}".format(self.password, command.strip())

        stdin, stdout, stderr = self.session.exec_command(command.strip() + "\n")
        stdout.channel.recv_exit_status()
        
        error = ""
        if stderr:
            error = "\n".join(stderr.readlines())
        
        output = '\n'.join([self.clean(line.rstrip()) for line in stdout.readlines()])
        output += error
        
        # replace traces of 'sudo enter password' from output
        output = output.replace("[sudo] password for {}: ".format(self.username), "")
        
        if pprint:
            self.pprint(output, pattern=pprint, end=end)

        return output
    
    def execute_script(self, path, pprint=0, end='', sudo=False, *args, **kwargs):
        # convert ~/ to absolute path for sftp
        script = self.resolve_path(path, local=True)
        remotepath = "/home/{}/{}".format(self.username, os.path.basename(script))

        # copy script to remote machine
        self.put(script, remotepath)

        # execute script on remote machine
        sudo = "sudo " if sudo else ""
        out = self.execute("{0}chmod 777 {1}; {0}{1}".format(sudo, remotepath), pprint=pprint, end=end, sudo=sudo, *args, **kwargs)
        
        # remove script from remote machine
        self.sftp.remove(remotepath)

        return out


    def write(self, command, postfix="\n", sudo=False):
        if command.startswith("sudo") or sudo:
            # if commands starts with sudo, then automatically enter password
            command = "echo {} | sudo -S {}".format(self.password, command.strip())

        # execute command normally
        self.stdin.write(command + postfix)
        self.history._stdin.append(command)

    def read(self, nbytes=2048, data="", bypass_sudo=True, repeat_last=False, clean=True, include_stdin=False):
        # receive data in buffers
        while True:
            if self.channel.recv_ready():
                data += self.channel.recv(nbytes).decode()
            else:
                break
        
        # logic to bypass sudo
        if "[sudo] password for" in data and bypass_sudo == True:
            # automatically enter password
            self.write_password()
            time.sleep(1)

            # read more from stdout after
            # password is written to stdin
            return self.read(data=data, bypass_sudo=False)
        
        # save stdout history
        output = ""
        for line in data.split("\n"):
            # if clean = True, use regex to get rid of colorful content
            line = self.clean(line.rstrip()) if clean else line.rstrip()
            
            # don't include executed command in stdout
            if include_stdin == False:
                try:
                    if line == self.history._stdin[-1]:
                        continue
                except: pass

            self.history._stdout.append(line)
            output += line+"\n"
        
        # logic to return data from history if output is empty
        if (not output.rstrip()) and (repeat_last == True):
            output = '\n'.join(self.history.stdout)

        return output.rstrip()