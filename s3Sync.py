#!/usr/bin/env python

import sys
import os


def get_state():
    dir = os.environ['HOME'] + '.s3sync'   

def usage():
    print("{} [command] [subcommands]\n".format(sys.argv[0]))
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current directory\n")
    
def main():
    if len(sys.argv) < 3:
        usage()

    if sys.argv[1] == "init":
        current_dir = os.getcwd()
        
    


if __name__ == '__main__':
    main()