import os
import stat


class ParseConfig:
    def __init__(self, config_file):
        self.root_dir = None
        self.db_location = None
        with open(config_file, 'r') as fh:
            for line in fh:
                if line[0] != '#' and line[0] != '\n':
                    line = line.replace(' ', '').replace('\n', '')
                    variable, value = line.split('=')
                    if variable == 'ROOT_DIR':
                        self.root_dir = value
                    if variable == 'DB_LOCATION':
                        self.db_location = value

        if self.root_dir is None:
            sys.exit("Error: config file -> {} no ROOT_DIR specified".format(
                config_file))

        if self.db_location is None:
            sys.exit("Error: config file -> {} no DB_LOCATION specified".
                     format(config_file))

        self.trackers_dir = self.db_location + '/trackers'

    def in_scope(self, target_dir):
        self.target_dir = target_dir
        if(os.path.commonpath([self.root_dir, self.target_dir])
           != self.root_dir):

            return False
        else:
            return True


def write_config(s3sync_config, home_dir):
    default_config = '#ROOT_DIR -  This field ensure s3sync can\'t \
        perform backup actions above a giving directory.\n' \
        '#SET to \'/\' (without quotes) for system wide backup privs.\n\n'\
        'ROOT_DIR={}\n\n' \
        '#s3sync will need a location to store file state information to' \
        'to detect changes in order to initiate uploads.\n' \
        '#The variable \'DB_LOCATION\' specifies the directory where this \
        information will be stored.\n\n' \
        'DB_LOCATION={}\n'.format(home_dir + '/s3syc_backupdir',
                                  home_dir + '/.s3sync')
    with open(s3sync_config, 'w') as fh:
        fh.write(default_config)
        return


def set_state():
    home_dir = os.environ['HOME']
    s3sync_dir = os.environ['HOME'] + '/' + '.s3sync'
    s3sync_config = home_dir + '/.s3sync/s3sync.config'
    s3tracker_dir = s3sync_dir + '/trackers'

    if os.path.isdir(s3sync_dir) is False:
        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC
        os.mkdir(s3sync_dir, mode)
        os.mkdir(s3tracker_dir, mode)
        write_config(s3sync_config, home_dir)
    else:
        if os.path.isfile(s3sync_config) is False:
            write_config(s3sync_config, home_dir)
    return s3sync_config
