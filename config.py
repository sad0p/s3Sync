

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as fh:
            for line in fh:
                if line[0] != '#' and line[0] != '\n':
                    variable, value = line.split('=')
                    if variable == "ROOT_DIR":
                        self.root_dir = value
                    if variable == "DB_LOCATION":
                        self.db_location = value            


def main():
    c = Config('./s3sync.config')
    print(c.root_dir)
    print(c.db_location)
    
if __name__ == '__main__':
    main()                   