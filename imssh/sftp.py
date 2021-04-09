def put(self, localpath, remotepath):
    sftp = self.session.open_sftp()
    
    if os.path.isdir(localpath):
        try:
            # test if remote_path exists
            sftp.chdir(remotepath) 
        except IOError:
            # create remote dir
            sftp.mkdir(remotepath)
        
        # copy file to remote one by one
        for file in os.listdir(localpath):
            self.put(os.path.join(localpath, file), os.path.join(remotepath, file))
    else:
        sftp.put(localpath, remotepath)
    
    sftp.close()

def get(self, remotepath, localpath, isdir=False):
    sftp = self.session.open_sftp()
    
    if isdir:
        # create local dir
        os.makedirs(localpath, exist_ok=True)
        
        # copy files from remote one by one
        for file in sftp.listdir(path=remotepath):
            self.get(os.path.join(remotepath, file), os.path.join(localpath, file))
    else:
        try:
            sftp.get(remotepath, localpath)
        except OSError:
            # exception means it's a directory
            if os.path.exists(localpath) and os.path.isfile(localpath) and os.path.getsize(localpath) == 0:
                # remove temporary file which is created by sftp
                os.remove(localpath)
            
            # recursively download directory
            self.get(remotepath, localpath, isdir=True)

    sftp.close()