import boto3
import json
import dirmonitor as dirmon


def get_que_list(que_dir):
    que = dict()
    que_list = dirmon.gen_file_list(que_dir)
    for item in que_list:
        que[item] = get_file_list(item)
    return que


def get_file_list(que_file):
    file_list = []
    with open(que_file, 'r') as fh:
        file_list = json.load(fh)
    return file_list


if __name__ == '__main__':
    print(get_que_list('/home/sad0p/.s3sync/ques'))
