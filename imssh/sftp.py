import os

class Sftp:

    def remote_dir_exists(self, path, sftp):
        try:
            # test if remote_path exists
            sftp.chdir(path) 
            return True
        except IOError:
            return False
    
    def resolve_path(self, path, local=False):
        if path.startswith("~/"):
            path = path.replace("~/", "")
            path = os.path.join("/home", self.localusername if local else self.username, path)
        return path

    def put(self, localpath, remotepath, create_dir=False):
        sftp = self.session.open_sftp()

        localpath = self.resolve_path(localpath, local=True)
        remotepath = self.resolve_path(remotepath, local=False)

        if os.path.isdir(localpath):
            if not self.remote_dir_exists(remotepath, sftp):
                sftp.mkdir(remotepath)

            # copy file to remote one by one
            for file in os.listdir(localpath):
                self.put(os.path.join(localpath, file), os.path.join(remotepath, file))
        else:
            # check if file name is explicitly passed
            if not os.path.basename(localpath) == os.path.basename(remotepath):
                # add remote path file name then
                remotepath = os.path.join(remotepath, os.path.basename(localpath))

            if create_dir:
                # check if reomte dir does not exists
                remotedir = os.path.dirname(remotepath)
                if not self.remote_dir_exists(remotedir, sftp):
                    # create remote dir
                    sftp.mkdir(remotedir)

            # copy file from local system to remote path
            sftp.put(localpath, remotepath)

        sftp.close()

    def get(self, remotepath, localpath, isdir=False, create_dir=True):
        sftp = self.session.open_sftp()

        localpath = self.resolve_path(localpath, local=True)
        remotepath = self.resolve_path(remotepath, local=False)

        if isdir:
            # create local dir
            os.makedirs(localpath, exist_ok=True)

            # copy files from remote one by one
            for file in sftp.listdir(path=remotepath):
                self.get(os.path.join(remotepath, file), os.path.join(localpath, file))
        else:
            # check if file name is explicitly passed
            if not os.path.splitext(os.path.basename(localpath))[1]:
                # add local path file name then
                localpath = os.path.join(localpath, os.path.basename(remotepath))

            if create_dir:
                localdir = os.path.dirname(localpath)
                os.makedirs(localdir, exist_ok=True)

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