import os
import time

class Scripts:
    def change_password(self, new_password=None, current_password=None, username=None):
        current_password = current_password or self.password
        new_password = new_password or self.password
        username = username or self.username

        if current_password == new_password:
            return True

        if (username == self.username) and (current_password != self.password):
            raise ValueError("current_password doesn't matches with self.password")
        
        cmd = "sudo echo -n; echo '{username}:{new_password}' | sudo chpasswd".format(
                username=username,
                new_password=new_password
            )
        
        self.execute(cmd)
        if "incorrect password attempt" in self.execute("sudo ls"):
            # this means password changed successfully!
            # update current password in the object
            self.password = new_password
            return True
        
        # return false if password is unchanged
        return False

    def execute_script(self, path, pprint=0, end='', sudo=False, clean_output=True, args=None):
        # convert ~/ to absolute path for sftp
        script = self.resolve_path(path, local=True)
        remotepath = "/home/{}/{}_{}".format(self.username, time.time(), os.path.basename(script))

        try:
            with open(script, "r") as s:
                with self.sftp.open(remotepath, "w") as f:
                    f.write(s.read())

            replace_output = lambda x: x.replace(remotepath, ("\n" if not x.startswith("/home") else "")+os.path.basename(script))

            # execute script on remote machine
            sudo = "sudo " if sudo else ""
            output = self.execute("{0}chmod 777 {1}; {0}{1}{2}".format(sudo, remotepath, ' '+' '.join(args) if args else ''), pprint=pprint, end=end, sudo=sudo, replace_output=replace_output if clean_output else None)

            return output
        except KeyboardInterrupt:
            pass
        except Exception:
            raise
        finally:
            # remove script from remote machine
            self.sftp.remove(remotepath)