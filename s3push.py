import os
import sys
import json
import logging
import boto3
from botocore.exceptions import ClientError
import s3hash
import config
import dirmonitor as dirmon
import s3object
import s3Sync


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


"""
    Duplicate code. See s3Sync.py
"""


def update_que(que_path, config_obj):
    tracker_object_dir = os.path.join(config_obj.db_location, 'objects')
    tracker_object_path = os.path.join(tracker_object_dir,
                                       os.path.basename(que_path))

    with open(tracker_object_path, 'r') as fh:
        tracker_object_meta_data = s3object.TrackerObject(**json.load(fh))
        os.remove(que_path)
        tracker_object_meta_data.sync_status = 'sync'
        s3Sync.update_tracker_object(tracker_object_path,
                                     tracker_object_meta_data)


def get_bucket_name():
    config_obj = config.ParseConfig()
    return config_obj.bucket_name


def bucket_exist(bucket_name, s3_object):
    bucket_list = s3_object.list_buckets()['Buckets']
    for bucket in bucket_list:
        if bucket['Name'] == bucket_name:
            return True
    return False


def upload(bucket_name, file_path, s3_object, logger):
    if bucket_exist(bucket_name, s3_object) is False:
        logger.info(f"Creating S3 Bucket {bucket_name}")
        make_bucket(bucket_name, s3_object, logger)
    try:
        response = s3_object.upload_file(file_path, bucket_name, file_path)
    except ClientError:
        logger.fatal(f"Failed to upload to {file_path} to {bucket_name}")
        sys.exit(1)
    logger.info(f"Uploaded {file_path} to bucket {bucket_name}")


def make_bucket(bucket_name, s3_object, logger):
    try:
        s3_object.create_bucket(Bucket=bucket_name)
    except ClientError:
        logger.fatal(f"Error creating bucket {bucket_name}")
        sys.exit(1)


def create_logger(push_log_path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh_logger = logging.FileHandler(push_log_path)
    logger_formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s:%(funcName)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    fh_logger.setFormatter(logger_formatter)
    logger.addHandler(fh_logger)
    return logger


def run():
    s3_object = boto3.client('s3')
    config_obj = config.ParseConfig()
    logger = create_logger(config_obj.push_log_path)

    ques = get_que_list(config_obj.ques_dir)

    for item in ques:
        file_list = ques[item]
        for f in file_list:
            upload(config_obj.bucket_name, f, s3_object, logger)
        update_que(item, config_obj)


if __name__ == '__main__':
    run()
