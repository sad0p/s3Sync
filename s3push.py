import os
import sys
import json
import boto3
import binascii
from botocore.exceptions import ClientError
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
    config_obj = config.ParseConfig()
    return config_obj.bucket_name


def bucket_exist(bucket_name, s3_object):
    bucket_list = s3_object.list_buckets()['Buckets']
    for bucket in bucket_list:
        if bucket['Name'] == bucket_name:
            return True
    return False


def upload(bucket_name, file_path, s3_object):
    if bucket_exist(bucket_name, s3_object) is False:
        make_bucket(bucket_name, s3_object)

    file_name = os.path.basename(file_path)
    try:
        response = s3_object.upload_file(file_path, bucket_name, file_name)
    except ClientError:
        print(f"Failed to upload to {file_path} to {bucket_name}")


def make_bucket(bucket_name, s3_object):
    try:
        s3_object.create_bucket(Bucket=bucket_name)
    except ClientError:
        sys.exit(f"Error creating bucket {bucket_name}")


if __name__ == '__main__':
    s3_object = boto3.client('s3')
    ques = get_que_list('/home/sad0p/.s3sync/ques')
    for item in ques:
        bucket_name = (s3hash.decode_path(
                        os.path.basename(item)).replace('/', '-')[1:].replace('_', '.'))
        file_list = ques[item]
        for f in file_list:
            upload(bucket_name, f, s3_object)
