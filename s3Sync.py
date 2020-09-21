#!/usr/bin/env python


import sys
import os
import stat 

import config 

def get_ignore_list(ignore_file):
    pass

def set_state():
    s3sync_dir = os.environ['HOME'] + '/' + '.s3sync'
    s3sync_config = s3sync_dir + '/' + 's3sync.config'
    home_dir = os.environ['HOME']
    
    if os.path.isdir(s3sync_dir) == False:
        os.mkdir(s3sync_dir)
        os.chmod(s3sync_dir, stat.S_IRUSR | stat.S_IWUSR)
        write_config(s3sync_config, home_dir)
    else:
        if os.path.isfile(s3sync_config) == False:
            write_config(s3sync_config, home_dir)

    return s3sync_config


def init(root_dir):
    if config.in_scope(root_dir) ==  False:
        sys.exit("[-] Error: Outside of ROOT_DIR ({}) scope".format(config.root_dir))

    ignore_file = root_dir + '/' + '.s3sync-ignore'
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
        init(options.root_dir)
        
    
if __name__ == '__main__':
    main()