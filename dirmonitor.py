import os
import sys
import s3hash


def gen_file_list(root_dir):

    file_list = []
    for dir_path, _, file_names in os.walk(root_dir, followlinks=False):
        for fname in file_names:
            wfname = os.path.join(dir_path, fname)
            file_list.append(wfname)
    return file_list


def create_tracker(hash_name, db_location):
    tracker_path = os.path.join(db_location, f'trackers/{hash_name}')
    open(tracker_path, 'x')
    return tracker_path


def create_tracker_object(hash_name, db_location):
    tracker_object_path = os.path.join(db_location, f'objects/{hash_name}')
    open(tracker_object_path, 'x')
    return tracker_object_path


def is_tracking(hash_name, db_location):
    file_list = gen_file_list(db_location)
    full_path = os.path.join(db_location, f'trackers/{hash_name}')
    for item in file_list:
        if item == full_path:
            return True
    return False
