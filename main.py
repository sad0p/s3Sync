#!/usr/bin/env python

import sys

def main():
    if len(sys.argv) < 4:
        usage()

def usage():
    print("{} [command] [subcommands]\n".format(sys.argv[0]))
    print("List of Commands:\n")
    print("init    --- start tracking and backing up files in current directory\n")

if __name__ == '__main__':
    main()