import os
import sys
import config
import ctypes
import signal
import logging


class S3Daemon():
    def __init__(self, config):
        self.INTERVAL = 10.0
        self.pid_file = os.path.join(config.db_location, 's3daemon.pid')

    def start(self):
        if self.is_running() is True:
            sys.exit(f"Daemon is running. Pidfile ({self.pid_file}) present.")

        if ctypes.CDLL(None).daemon(0, 0) < 0:
            sys.exit(f"Failed to daemonize")

        self.pid = os.getpid()
        with open(self.pid_file, 'w') as self.fh:
            self.fh.write(f'{self.pid}')

        self.run()

    def stop(self):
        if self.is_running is False:
            sys.exit(
             f"Daemon is not running. Pidfile ({self.pid_file}) not present")

        with open(self.pid_file, 'r') as self.fh:
            self.pid = int(self.fh.read())

        os.kill(self.pid, signal.SIGTERM)
        os.remove(self.pid_file)

    def is_running(self):
        return os.path.isfile(self.pid_file)

    def run(self):
        signal.pause()


def usage():
    sys.exit(f"{sys.argv[0]} start | stop | restart")


def main():

    if len(sys.argv) != 2:
        usage()
    config_file = os.path.join(os.getenv('HOME'), '.s3sync/s3sync.config')
    daemon = S3Daemon(config.ParseConfig(config_file))

    if sys.argv[1] == "start":
        daemon.start()

    elif sys.argv[1] == "stop":
        daemon.stop()

    elif sys.argv[1] == "restart":
        pass
    else:
        usage()


if __name__ == '__main__':
    main()
