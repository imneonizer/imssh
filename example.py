import imssh
import time
import re
import traceback
import sys

# @imssh.sync
def target(host):
    try:
        if not host[0].isdigit(): return

        s = imssh.connect(username="nvidia", password="nvidia", host=host)
        # s.put("scripts/install_jtop.sh", "/home/nvidia/install_jtop.sh")
        # s.execute("sudo chmod +x /home/nvidia/install_jtop.sh")
        # s.execute("sudo /home/nvidia/install_jtop.sh", 1, end="\n")
        s.sftp.remove("/home/nvidia/install_jtop.sh")

    except Exception as e:
        print(e)
        pass

with open("hosts.ini", "r") as f:
    hosts =  f.readlines()
    res = imssh.map(target, hosts)