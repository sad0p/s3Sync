import os
import sys


def gen_file_list(rootdir):

    file_list = []
    for dir_path, dir_name, file_names in os.walk(rootdir, followlinks=False):
        for fname in file_names:
            wfname = os.path.join(dir_path, fname)
                file_list.append(wfname)
    return file_list


def create_tracker(hash_name, db_location):

    full_path = db_location + '/' + hash_name
    with open(full_name , 'w') as fh:
        return fd, full_path

        
def is_tracking(hash_name, db_location):
    file_list = gen_file_list(db_location)    
    for item in file_list:
        if item == hash_name:
            return true
    return False