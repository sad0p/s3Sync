import os
import sys
import s3hash

def gen_hash_db(file_list):

    hash_db = {}
    for item in file_list:
        item_hash = s3hash.genfile_hash(item)
        hash_db[item] = item_hash
    return hash_db

def gen_file_list(root_dir):

    file_list = []
    for dir_path, dir_name, file_names in os.walk(root_dir, followlinks=False):
        for fname in file_names:
            wfname = os.path.join(dir_path, fname)
            file_list.append(wfname)
    return file_list


def create_tracker(hash_name, db_location):

    full_path = db_location + '/' + hash_name
    open(full_path , 'x')
    return full_path

        
def is_tracking(hash_name, db_location):

    file_list = gen_file_list(db_location)    
    full_path = db_location + '/' + hash_name
    for item in file_list:
        if item == full_path:
            return True
    return False

