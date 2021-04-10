# usage: python launcher.py -c ls -i hosts

import os, sys
import argparse
import paramiko
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import imssh

class ImsshLauncher:
    def launch(self, device):
        username = device.username or self.args.username
        password = device.password or self.args.password
        port = device.port or self.args.port
        host = device.host
        target = "{}@{}:{}".format(username, host, port)

        if None in [username, password, host, port]:
            if self.args.verbose:
                print("[ERROR] invalid target: {}".format(target))
            return

        try:
            s = imssh.connect(username=username, password=password, host=host, port=port)

            if "script:" in self.args.command:
                script = self.args.command.replace("script:", "")
                args = ""
                if " " in script:
                    script, args = script.split(" ", 1)

                if self.args.verbose:
                    print("[EXEC] script:{}, args:{}, target:{}".format(script, args, target))
                s.execute_script(script, args=[args], pprint=self.args.pprint)
            else:
                if self.args.verbose:
                    print("[EXEC] command:{}, target:{}".format(self.args.command, target))
                s.execute(self.args.command, self.args.pprint)

        except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.NoValidConnectionsError):
            pass
        except Exception as e:
            print(traceback.format_exc())

    def run(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--command", required=True, help="command to execute on remote machines")
        ap.add_argument("-i", "--input", required=False, default="", help="path to hosts file")
        ap.add_argument("-u", "--username", required=False, default=None, help="default username for hosts")
        ap.add_argument("-p", "--password", required=False, default=None, help="default password for hosts")
        ap.add_argument("-t", "--target", required=False, help="target machine")
        ap.add_argument("-v", "--verbose", required=False, type=bool, default=False, help="verbose")

        ap.add_argument("--pprint", required=False, default=3, type=int, help="print pattern")
        ap.add_argument("--port", required=False, default=22, help="port")
        ap.add_argument("--timeout", required=False, default=5, type=int, help="ssh connection timeout if not reachable")
        self.args = ap.parse_args()

        if "script:" in self.args.command:
            script = self.args.command.replace("script:", "")
            assert os.path.exists(script), "script file: {} doesn't exists".format(script)

        if self.args.target:
            if (not self.args.username) and (not self.args.password):
                print("[ERROR] username and password required for target: {}".format(self.args.target))
                exit(1)

            # this means to execute command on a single device
            target = "{}@{}:{} {}".format(self.args.username, self.args.target, self.args.port, self.args.password)
            if self.args.verbose:
                print("[INFO] connecting to target: {}".format(target))

            self.launch(imssh.Host(target))
        
        else:
            hosts, group = self.args.input, "all"
            if ":" in self.args.input:
                hosts, group = self.args.input.split(":")

            assert os.path.exists(hosts), "hosts file: '{}' doesn't exists".format(hosts)

            #execute on multiple devices
            with imssh.open(hosts) as hosts:
                imssh.map(target=self.launch, args=hosts.get(group))

if __name__ == "__main__":
    ImsshLauncher().run()