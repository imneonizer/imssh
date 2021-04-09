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