import sys
import hashlib
import base64


def gen_hash_db(file_list):

    hash_db = dict()
    for item in file_list:
        item_hash = genfile_hash(item)
        hash_db[item] = item_hash
    return hash_db


def genfile_hash(target_file):

    with open(target_file, 'rb') as fh:
        hash_obj = hashlib.sha256()
        content = fh.read()
        hash_obj.update(content)
    return hash_obj.hexdigest()


def encode_path(path):
    return base64.b64encode(path.encode()).decode()


def decode_path(path):
    return base64.b64decode(path.encode()).decode()
