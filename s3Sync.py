#!/usr/bin/env python

import os
import sys
import stat 
import json

import config
import dirmonitor as dirmon
import s3hash

def purged_of_ignored(file_list, ignore_file):

    remove_items = []
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
                


def set_state():

    s3sync_dir = os.environ['HOME'] + '/' + '.s3sync'
    s3sync_config = s3sync_dir + '/' + 's3sync.config'
    homedir = os.environ['HOME']
    
    if os.path.isdir(s3sync_dir) == False:
        os.mkdir(s3sync_dir)
        os.chmod(s3sync_dir, stat.S_IRUSR | stat.S_IWUSR)
        write_config(s3sync_config, homedir)
    else:
        if os.path.isfile(s3sync_config) == False:
            write_config(s3sync_config, homedir)

    return s3sync_config


def re_init(target_dir, config_obj, verbose=True):
    pass
    

def init(target_dir, config_obj, verbose=True):
    
    hash_db = {}
    
    if config.in_scope(config_obj.root_dir, target_dir) ==  False:
        sys.exit("[-] Error: Outside of ROOT_DIR ({}) scope".format(config_obj.root_dir))

    target_dir_hash = s3hash.genpath_hash(target_dir)
    if dirmon.is_tracking(target_dir_hash, config_obj.db_location) == True:
        sys.exit("[-] Error: {} is already being tracked".format(target_dir))
    else:
        print("[+] Initiating tracking of {}".format(target_dir))
        tracker_path = dirmon.create_tracker(target_dir_hash, config_obj.db_location)
        ignore_file = target_dir + '/' + '.s3ignore'

        if os.path.exists(ignore_file):
            target_dir_list = purged_of_ignored(dirmon.gen_file_list(
                target_dir), ignore_file)
        else:
            target_dir_list = dirmon.gen_file_list(target_dir) + '/' + '.s3ignore'

        with open(tracker_path, 'w') as fh:
            for item in target_dir_list:
                if verbose == True:
                    print("[+] tracking -> {}".format(item))
                item_hash = s3hash.genfile_hash(item)
                hash_db[item] = item_hash
                json.dump(hash_db, fh)
                #fh.write('{} -> {}\n'.format(item, item_hash))
        return


def usage():

    print("{} [command] [subcommands]\n".format(sys.argv[0]))
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current directory\n")



    
def main():

    opt_init_dir = None
    if len(sys.argv) < 2:
        usage()
        sys.exit()
        
    s3sync_config = set_state()
    config_obj = config.Parse(s3sync_config)
    
    if sys.argv[1] == 'init':
        if len(sys.argv) > 2:
            opt_init_dir = sys.argv[2]
        else:
            opt_init_dir = os.getcwd()
            
        init(opt_init_dir, config_obj)
   
    
if __name__ == '__main__':
    main()