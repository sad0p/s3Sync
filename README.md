# s3sync (alpha)
A backup/synchronization script for AWS S3 Bucket service.
You can configure the script to maintain copies of certain files or directories on your computer in Amazon AWS S3 Bucket.

# Tracking a directory

./s3sync init &lt;target-directory&gt;

# Manually updating the s3sync records of directory changes

./s3sync update

# Displaying currently tracked directories

![Demo Animation](../assets/tracker-ls.png?raw=true)
./s3sync tracker ls

# Removing directories that are currently being tracked by s3sync

./s3sync tracker rm [tracker]

# Moving changes to s3 bucket is carried out by s3daemon.py
# As of right now (aplha), only one bucket can be specified in the configuration.

#initializing the s3daemon

python s3daemon.py start

# stopping s3daemon

python s3daemon.py stop

# General info

# $(HOME)/.s3sync/ is the location for the config, logs and records of file changes.
# daemon.log and push.log can let you see the activity of the s3daemon.
# the default interval for checking on directory changes is 10 seconds. This is not configurable from the configuration file at this time.

# If you so desire, you can edit s3daemon.py (line 14) INTERVAL to be equal to the desired interval (measured in seconds).


# Ignore files.
# Similar to .gitignore, you can do .s3ignore where specific files can be specified or an entire subdirectory (absolute path).
