import pysftp

# get_r() is a recursive get
# put_r() is a recursive put
# get() and put() are for single files
# get_d() and put_d() are for single directories
# getfo() and putfo() are for single files, but return file-like objects
# getfo_d() and putfo_d() are for single directories, but return file-like objects
# listdir() lists the contents of a remote directory
# chdir() changes the current remote directory
# mkdir() creates a remote directory
# rmdir() removes a remote directory
# remove() removes a remote file
# rename() renames a remote file or directory
# stat() returns information about a remote file
# symlink() creates a symbolic link on the remote server
# readlink() returns the target of a symbolic link on the remote server

# To run something like tar through pysftp, you can use the following:
# sftp.execute('tar -xzf file.tar.gz')


def deploy():
    # have pysftp piggyback off of paramiko
    cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None  # Disable host key checking (only for trusted servers)
    with pysftp.Connection(
        "192.168.68.64", username="alfred", password="njit#IT#490", cnopts=cnopts
    ) as sftp:
        # First, set the working directory to the Desktop or wherever we have our files.
        sftp.cwd("/home/alfred/Desktop")
        x = sftp.pwd
        print(f"Current working directory: {x}")
        files = sftp.listdir()
        print("files in the remote directory:")
        for file in files:
            print(file)
        # sftp.get_r("comegetme", "/home/alfred/Desktop/Deployment", True)
        # sftp.execute("tar -czvf comegetme.tar.gz comegetme")
        sftp.close()


if __name__ == "__main__":
    deploy()
