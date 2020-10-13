#!/usr/bin/env python

import os
import sys
import stat
import json
import boto3
import itertools

import config
import dirmonitor as dirmon
import s3hash


def purged_of_ignored(file_list, ignore_file):
    remove_items = []

    if os.path.isfile(ignore_file) is False:
        return file_list

    with open(ignore_file, 'r') as fh:
        purge_items = [x.strip('\n') for x in fh.readlines()]

    for item in purge_items:
        if os.path.isdir(item):
            for file_item in file_list:
                if os.path.commonpath([item, file_item]) == item:
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


def name_from_path(path):
    count = 0
    new_path = path.rstrip('/')
    for i, c in enumerate(new_path):
        if c == '/':
            count = i
    return new_path[count + 1:]


def update(config_obj):
    update_files = []
    trackers_dir = config_obj.trackers_dir
    tracker_list = dirmon.gen_file_list(trackers_dir)

    for tracker in tracker_list:
        print("Tracker -> {}".format(tracker))
        update_files.extend(update_tracker(tracker))

    if len(update_files) > 0:
        print("[+} In que for uploading to s3 server")
        for item in update_files:
            print("{}".format(item))


def update_tracker(tracker_path, verbose=True, initial=False):
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
        and allow the code the to simply update the tracker. This reduces
        duplicate code in init() and update_tracker().
        """
        try:
            hash_db = json.load(fh) if initial is False else {}
        except(json.JSONDecodeError):
            pass
        target_dir_decode = s3hash.decode_path(name_from_path(tracker_path))
        print("Tracker path -> {}".format(target_dir_decode))

    ignore_file = target_dir_decode + '/' + '.s3ignore'
    file_list = purged_of_ignored(dirmon.gen_file_list(target_dir_decode),
                                  ignore_file)

    new_hash_db = s3hash.gen_hash_db(file_list)
    added_files = (new_hash_db.keys()
                   - hash_db.keys() if initial is False else ())

    removed_files = hash_db.keys() - new_hash_db.keys()

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


def tracker_ls(config_obj):
    tracker_list_encoded = dirmon.gen_file_list(config_obj.trackers_dir)

    for i, v in enumerate(tracker_list_encoded):
        tracker_list_encoded[i] = name_from_path(v)

    tracker_list_decoded = [s3hash.decode_path(x)
                            for x in tracker_list_encoded]

    print('{:<50}{:<50}{:<20}{:<20}{:<20}'.format("Tracker", "Associated",
                                                  "Created", "modified",
                                                  "Remote-Sync"))

    for (e, d) in zip(tracker_list_encoded, tracker_list_decoded):
        print('{:<50}{:<30}'.format(e, d))
    pass


def init(target_dir, config_obj, verbose=True):
    hash_db = dict()

    if config_obj.in_scope(target_dir) is False:
        sys.exit("[-] Error: Outside of ROOT_DIR ({}) scope".format(
            config_obj.root_dir))

    target_dir_encode = s3hash.encode_path(target_dir)
    if dirmon.is_tracking(target_dir_encode, config_obj.db_location) is True:
        sys.exit("[-] Error: {} is already being tracked".format(target_dir))
    else:
        print("[+] Initiating tracking of {}".format(target_dir))
        tracker_path = dirmon.create_tracker(target_dir_encode,
                                             config_obj.db_location)
        update_tracker(tracker_path, config_obj, True)
        return


def usage():
    print("{} [command] [subcommands]\n".format(sys.argv[0]))
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current "
          "directory")
    print("update  --- updates for the directory trackers for changes "
          "and pushes additions or file modifications to s3")


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
        pass


if __name__ == '__main__':
    main()
