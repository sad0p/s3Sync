import os
import stat
import s3hash


class ParseConfig:
    def __init__(self, config_file=None):
        self.root_dir = None
        self.db_location = None
        self.bucket_name = None
        self.config_file = config_file

        if self.config_file is None:
            self.home_dir = os.getenv('HOME')
            self.config_file = os.path.join(
                                self.home_dir, '.s3sync/s3sync.config')

        with open(self.config_file, 'r') as self.fh:
            for self.line in self.fh:
                if self.line[0] != '#' and self.line[0] != '\n':
                    self.line = self.line.replace(' ', '').replace('\n', '')
                    self.variable, self.value = self.line.split('=')
                    if self.variable == 'ROOT_DIR':
                        self.root_dir = self.value
                    if self.variable == 'DB_LOCATION':
                        self.db_location = self.value
                    if self.variable == 'BUCKET_NAME':
                        self.bucket_name = self.value

        if self.root_dir is None:
            sys.exit(f"Error: config file -> {self.config_file} no ROOT_DIR")

        if self.db_location is None:
            sys.exit(
             f"Error: config file -> {self.config_file} no DB_LOCATION")

        if self.bucket_name is None or self.bucket_name == '':
            self.user = os.getenv("USER")
            self.bucket_name = f's3sync-{s3hash.encode_path(self.user)}'
        self.trackers_dir = os.path.join(self.db_location, 'trackers')

    def in_scope(self, target_dir):
        self.target_dir = target_dir
        if(os.path.commonpath([self.root_dir, self.target_dir])
           != self.root_dir):

            return False
        else:
            return True


def write_config(s3sync_config, home_dir):
    default_config = '#ROOT_DIR -  This field ensures s3sync can\'t \
        perform backup actions above a giving directory.\n' \
        '#SET to \'/\' (without quotes) for system wide backup privs.\n\n'\
        f'ROOT_DIR={home_dir}\n\n' \
        '#s3sync will need a location to store file state information to' \
        'to detect changes in order to initiate uploads.\n' \
        '#The variable \'DB_LOCATION\' specifies the directory where this ' \
        'information will be stored.\n\n' \
        f'DB_LOCATION={home_dir}/.s3sync\n' \
        'BUCKET_NAME=\n'

    with open(s3sync_config, 'w') as fh:
        fh.write(default_config)
        return


def set_state():
    home_dir = os.environ['HOME']
    s3sync_dir = os.path.join(home_dir, '.s3sync')
    s3sync_sub_dirs_name = ['trackers', 'objects', 'ques']

    s3sync_config = os.path.join(s3sync_dir, 's3sync.config')
    if os.path.isdir(s3sync_dir) is False:
        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC
        os.mkdir(s3sync_dir, mode)

        for item in s3sync_sub_dirs_name:
            os.mkdir(os.path.join(s3sync_dir, item), mode)
        write_config(s3sync_config, home_dir)
    else:
        if os.path.isfile(s3sync_config) is False:
            write_config(s3sync_config, home_dir)
    return s3sync_config
