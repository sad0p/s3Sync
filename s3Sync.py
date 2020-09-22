#!/usr/bin/env python

import os
import sys
import stat 

import config
import dirmonitor as dirmon
import s3hash

def get_ignore_list(ignore_file):

    pass



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


def init(target_dir, config_obj):
    if config_obj.in_scope(target_dir) ==  False:
        sys.exit("[-] Error: Outside of ROOT_DIR ({}) scope".format(config_obj.root_dir))

    target_dir_hash = s3hash.genpath_hash(target_dir)
    if dirmon.is_tracking(target_dir_hash, config_obj.db_location) == True:
        sys.exit("[-] Error: {} is already being tracked".format(target_dir))
    else:
        print("[+] Initiating tracking of {}".format(target_dir))
        return
    #ignore_file = rootdir + '/' + '.s3sync-ignore'
    #if os.path.isfile(ignore_file) == True:
    #    ig_files, ig_dirs = get_ignore_list(ignore_file)
    
    
    

def usage():
    print("{} [command] [subcommands]\n".format(sys.argv[0]))
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current directory\n")
    
def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit()
        
    s3sync_config = set_state()
    options = config.Parse(s3sync_config)
    
    if sys.argv[1] == 'init':
        init(options.rootdir)
        
    
if __name__ == '__main__':
    main()