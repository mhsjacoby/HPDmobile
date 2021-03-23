import os

def mylistdir(directory, bit='', end=True):
    filelist = os.listdir(directory)
    if end:
        return [x for x in filelist if x.endswith(f'{bit}') and not x.endswith('.DS_Store') and not x.startswith('Icon')]
    else:
         return [x for x in filelist if x.startswith(f'{bit}') and not x.endswith('.DS_Store') and not x.startswith('Icon')]
        
def make_storage_directory(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir
