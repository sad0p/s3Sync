import os
import json
import boto3
import s3hash
import config
import dirmonitor as dirmon


def get_que_list(que_dir):
    que = dict()
    que_list = dirmon.gen_file_list(que_dir)
    for item in que_list:
        # s3hash.decode_path(os.path.basename(item))
        que[item] = get_file_list(item)
    return que


def get_file_list(que_file):
    file_list = []
    with open(que_file, 'r') as fh:
        file_list = json.load(fh)
    return file_list


def get_bucket_name():
    config_obj = config.ParseConfig('/home/sad0p/.s3sync/s3sync.config')
    return config_obj.bucket_name

if __name__ == '__main__':
    print(get_bucket_name())