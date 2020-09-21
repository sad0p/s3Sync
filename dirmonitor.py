import os
import sys

def gen_file_list(rootdir):
    file_list = []
    for dirpath, dirname, filenames in os.walk(rootdir, followlinks=False):
        for fname in filenames:
            wfname = os.path.join(dirpath, fname)
                file_list.append(wfname)
    return file_list

    