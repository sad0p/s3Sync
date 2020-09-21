import os

class Parse:
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

        if self.root_dir == '':
            print("Error: config file -> {} no ROOT_DIR specified".format(config_file))
        if self.db_location == '':
            print("Error: config file -> {} no DB_LOCATION specified".format(config_file))
        

def write_config(s3sync_config, home_dir):
    default_config = '#ROOT_DIR -  This field ensure s3sync can\'t perform backup actions above a giving directory.\n' \
        '#SET to \'/\' (without quotes) for system wide backup privilages.\n\n' \
        'ROOT_DIR={}\n\n' \
        '#s3sync will need a location to store file state information to detect changes in order to initiate uploads.\n' \
        '#The variable \'DB_LOCATION\' specifies the directory where this information will be stored.\n\n' \
        'DB_LOCATION={}\n'.format(home_dir + '/s3syc_backupdir', home_dir + '/' + '.s3sync')
    
    with open(s3sync_config, 'w') as fh:
        fh.write(default_config)
    fh.close()
    return

def in_scope(root_dir):
#    if len(root_dir) <= len(cwd):
#        element = 0
#        for c in root_dir:
#            if cwd[element] != c:
#                return False
#            element = element + 1
#    else:
#        return False
#    return True 
    if os.path.commonpath([root_dir, os.getcwd()]) != root_dir:
        return False
    else:
        return True
    