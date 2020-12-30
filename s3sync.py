#!/usr/bin/env python

import os
import sys
import stat
import json
import time
import itertools
import config
import s3hash
import s3object
import dirmonitor as dirmon


def que_files(file_list, tracker, config_obj):
    qued_tracker_name = os.path.basename(tracker)
    qued_tracker_dir = os.path.join(config_obj.db_location, 'ques')
    qued_tracker_path = os.path.join(qued_tracker_dir, qued_tracker_name)
    with open(qued_tracker_path, 'w') as fh:
        json.dump(file_list, fh)


def purged_of_ignored(file_list, ignore_file):
    remove_items = []

    if os.path.isfile(ignore_file) is False:
        return file_list

    with open(ignore_file, 'r') as fh:
        purge_items = [x.strip('\n') for x in fh.readlines()]

    for item in purge_items:
        if os.path.isdir(item):
            for file_item in file_list:
                if (os.path.commonpath([item, file_item])
                   == os.path.abspath(item)):
                    remove_items.append(file_item)
        else:
            try:
                file_list.remove(item)
            except(ValueError):
                pass

    if len(remove_items) > 0:
        for rm_item in remove_items:
            del file_list[file_list.index(rm_item)]
    return file_list


def path_to_tracker(target_path, config_obj):
    tracker = (config_obj.tracker_dir
               + s3hash.encode_path(target_path))
    return tracker


def update(config_obj):
    update_files = []
    update_tracker_object_list = []
    trackers_dir = config_obj.trackers_dir
    tracker_list = dirmon.gen_file_list(trackers_dir)

    for tracker in tracker_list:
        print(f"Tracker -> {tracker}")
        files_in_tracker = update_tracker(tracker)

        if len(files_in_tracker) > 0:
            update_tracker_object_list.append(tracker)
            que_files(files_in_tracker, tracker, config_obj)
            update_files.extend(files_in_tracker)

    if len(update_files) > 0:
        print("[+] In que for uploading to s3 server")
        for item in update_files:
            print(f"{item}")

        for item in update_tracker_object_list:
            tracker_oject_name = os.path.basename(item)
            tracker_object_dir = os.path.join(config_obj.db_location,
                                              'objects')

            tracker_object_path = os.path.join(tracker_object_dir,
                                               tracker_oject_name)

            with open(tracker_object_path, 'r') as fh:
                tracker_object_meta_data = s3object.TrackerObject(
                                            **json.load(fh))

            os.remove(tracker_object_path)

            tracker_object_meta_data.modified = time.strftime(
                                                     "%m/%d/%Y, %H:%M:%S")

            tracker_object_meta_data.sync_status = 'in-que'
            update_tracker_object(tracker_object_path,
                                  tracker_object_meta_data)
        return True
    return False


def update_tracker_object(tracker_object_path, tracker_object_meta_data):
    with open(tracker_object_path, 'w') as fh:
        json.dump(tracker_object_meta_data.__dict__, fh)


def update_tracker(tracker_path, config_obj=None, initial=False):
    hash_db = dict()
    new_hash_db = dict()
    removed_hash_db = dict()
    changed_hash_db = dict()
    added_hash_db = dict()
    update_files = []

    mode = 'r' if initial is False else 'w'
    with open(tracker_path, mode) as fh:
        """
        In the event the tracker is empty because the init() function
        uses the update_tracker() function to simply fill in filepath:hash
        data, we look for the JSONDecodeError exception in such a case
        and allow the code to simply update the tracker. This reduces
        duplicate code in init() and update_tracker().
        """
        try:
            hash_db = json.load(fh) if initial is False else {}
        except(json.JSONDecodeError):
            pass
        target_dir_decode = s3hash.decode_path(os.path.basename(tracker_path))
        print(f"Tracker path -> {target_dir_decode}")

    ignore_file = os.path.join(target_dir_decode, '.s3ignore')
    file_list = purged_of_ignored(dirmon.gen_file_list(target_dir_decode),
                                  ignore_file)

    new_hash_db = s3hash.gen_hash_db(file_list)
    added_files = (new_hash_db.keys()
                   - hash_db.keys() if initial is False else ())

    removed_files = hash_db.keys() - new_hash_db.keys()

    if initial is True:
        que_files(file_list, tracker_path, config_obj)

    # files removed
    if len(removed_files) > 0:
        for item in removed_files:
            removed_hash_db[item] = hash_db[item]
        for k, v in removed_hash_db.items():
            print("{} -> {} removed".format(k, v))

    # new files added
    if len(added_files) > 0:
        for item in added_files:
            update_files.append(item)
            added_hash_db[item] = new_hash_db[item]

        for k, v in added_hash_db.items():
            print("{} -> {} added".format(k, v))

    # files that changed
    for k, v in hash_db.items():
        if k not in added_hash_db and k not in removed_hash_db:
            if new_hash_db[k] != hash_db[k]:
                update_files.append(k)
                changed_hash_db[k] = new_hash_db[k]

    for k, v in changed_hash_db.items():
        print("{} -> {} changed".format(k, v))

    # delete the old tracker and create new one
    os.remove(tracker_path)
    with open(tracker_path, 'w') as fh:
        json.dump(new_hash_db, fh)

    # return list of files to be updated server side
    if len(update_files) > 0:
        for item in update_files:
            print("{} updating".format(item))
    return update_files


def tracker_rm(config_obj, tracker):
    tracker_object_path = f'{config_obj.db_location}/objects/{tracker}'
    tracker_path = f'{config_obj.db_location}/trackers/{tracker}'
    os.remove(tracker_object_path)
    os.remove(tracker_path)


def tracker_ls(config_obj):
    tracker_list_encoded = dirmon.gen_file_list(config_obj.trackers_dir)

    for i, v in enumerate(tracker_list_encoded):
        tracker_list_encoded[i] = os.path.basename(v)

    tracker_list_decoded = [s3hash.decode_path(x)
                            for x in tracker_list_encoded]

    for (e, d) in zip(tracker_list_encoded, tracker_list_decoded):
        associated_object = f'{config_obj.db_location}/objects/{e}'
        with open(associated_object, 'r') as fh:
            tracker_object_meta_data = s3object.TrackerObject(**json.load(fh))

        print(f'Tracker: {e}\nAssociated-With: {d}\n'
              f'Created:{tracker_object_meta_data.created}\n'
              f'Modified: {tracker_object_meta_data.modified}\n'
              f'Remote-Sync: {tracker_object_meta_data.sync_status}\n')


def init(target_dir, config_obj, verbose=True):
    hash_db = dict()

    if config_obj.in_scope(target_dir) is False:
        sys.exit(f"[-] Error: Outside of ROOT_DIR ({config_obj.root_dir})")

    if not os.path.exists(target_dir):
        sys.exit(f"[-] Error: {target_dir} does not exist")

    target_dir_encode = s3hash.encode_path(target_dir)
    if dirmon.is_tracking(target_dir_encode, config_obj.db_location) is True:
        sys.exit(f"[-] Error: {target_dir} is already being tracked")
    else:
        print("[+] Initiating tracking of {}".format(target_dir))
        tracker_path = dirmon.create_tracker(target_dir_encode,
                                             config_obj.db_location)

        update_tracker(tracker_path, config_obj, initial=True)

        tracker_object_path = dirmon.create_tracker_object(
                              target_dir_encode, config_obj.db_location)

        tracker_object_time = {
                               'created': time.strftime("%m/%d/%Y, %H:%M:%S"),
                               'modified': time.strftime("%m/%d/%Y, %H:%M:%S"),
                               'sync_status': 'in-que'
                              }

        tracker_object_meta_data = s3object.TrackerObject(
                                   **tracker_object_time)
        update_tracker_object(tracker_object_path, tracker_object_meta_data)
        return


def usage():
    print(f"{sys.argv[0]} [command] [subcommands]\n")
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current "
          "directory")
    print("update  --- updates the directory trackers for changes ")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit()

    s3sync_config = config.set_state()
    config_obj = config.ParseConfig(s3sync_config)

    if sys.argv[1] == 'init':
        opt_init_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
        init(opt_init_dir, config_obj)

    if sys.argv[1] == 'update':
        update(config_obj)

    if sys.argv[1] == 'tracker' and sys.argv[2] == 'ls':
        tracker_ls(config_obj)

    if sys.argv[1] == 'tracker' and sys.argv[2] == 'rm':
        if len(sys.argv) < 5:
            tracker_rm(config_obj, sys.argv[3])
        else:
            sys.exit("supply tracker:"
                     f"{sys.argv[0]} tracker rm [tracker] (without brackets)")


if __name__ == '__main__':
    main()
