#This document is a journaling of my thoughts and considerations that came up in designing and
#writing this application. Should someone seek to extend the code or understand my technical   # #perspectives in terms of what I was trying to achieve, this document might be useful.

- Goals
    + Enable the user to select which directory to monitor/backup in a fashion similar that of
      'git init'.
        ++ Also provide functionality to exclude files and subdirectories.
    + Provide a local scope for home directories, aswell as a global scope for the entire system.
        ++ Terminology "entire system" denotes directories and files outside of a non-root user home
        directory.

    + Monitoring can be done through a cron entry.
        ++ The application performs the cron entry, but configuration is done through the command line  or a configuration file.
    
    + Alternative monitoring methodology is to have the script run as a daemon.
        ++ Possible con is having hash data on files in memory for a large amount of files
        can hog resources, this could be mitigates by simply writing the data to disk.