import pysftp

def test():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # c_info = {'host':'192.168.1.103', 'username':'pi', 'password':'sensor', cnopts: cnopts}
    with pysftp.Connection('192.168.1.103', username='pi', password='sensor', cnopts = cnopts) as sftp:
        sftp.get_d('audio', 'audio', preserve_mtime=True)

if __name__ == "__main__":
    test()