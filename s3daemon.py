#!/usr/bin/env python

import os
import sys
import time
import argparse
import config
import ctypes
import signal
import s3logger
import s3sync
import s3push


class S3Daemon():
    def __init__(self, config, debug):
        self.INTERVAL = 10
        self.pid_file = os.path.join(config.db_location, 's3daemon.pid')
        self.logger = None
        self.config_obj = config
        self.debug = debug

        if self.debug is False:
            self.logger = s3logger.create_logger(config.daemon_log_path)
        else:
            self.logger = s3logger.create_logger()

    def start(self):
        if self.is_running() is True:
            self.logger.warning(
                f"Daemon is running. Pidfile ({self.pid_file}) present.")
            sys.exit(1)

        if self.debug is False:
            if ctypes.CDLL(None).daemon(0, 0) < 0:
                self.logger.warning(f"Failed to daemonize")
                sys.exit(1)

        self.pid = os.getpid()
        with open(self.pid_file, 'w') as self.fh:
            self.fh.write(f'{self.pid}\n')
        self.logger.info("started daemonization")
        self.run()

    def stop(self):
        if self.is_running() is False:
            self.logger.warning(
             f"Daemon is not running. Pidfile ({self.pid_file}) not present")
            sys.exit(1)

        with open(self.pid_file, 'r') as self.fh:
            self.pid = int(self.fh.read().strip('\n'))

        self.logger.info(
            f"Terminating daemon with pid {self.pid} in {self.pid_file}")
        try:
            os.kill(self.pid, signal.SIGTERM)
        except(ProcessLookupError):
            self.logger.warning(
                "Daemon either crashed or was manually stopped")
        os.remove(self.pid_file)

    def is_running(self):
        if os.path.isfile(self.pid_file) is True:
            with open(self.pid_file, 'r') as self.fh:
                self.pid = int(self.fh.read().strip('\n'))
            if os.path.isdir(f'/proc/{self.pid}') is True:
                return True
            else:
                self.logger.warning(
                 f"pidfile -> {self.pid_file} present "
                 "but the PID isn't assoicated with any running process")
                os.remove(self.pid_file)
                return False
        else:
            return False

    def run(self):
        signal.signal(signal.SIGTERM, self.stop)
        while True:
            time.sleep(self.INTERVAL)
            self.logger.info("checking for updates")

            if (s3sync.update(self.config_obj) is True or
                    s3push.get_que_list(self.config_obj.ques_dir)):

                self.logger.info("Updates present")
                s3push.run()
            else:
                self.logger.info("No updates present at this time")


def main():
    parser = argparse.ArgumentParser(
                                description="start or stop s3sync daemon")

    parser.add_argument('-c', '--control',
                        help="issue 'start' or 'stop' command as a argument")

    parser.add_argument('--debug', action='store_true', default=False,
                        help="prints debug information to the terminal")

    args = parser.parse_args()
    config_file = os.path.join(os.getenv('HOME'), '.s3sync/s3sync.config')
    daemon = S3Daemon(config.ParseConfig(config_file), args.debug)

    if args.control == "start":
        daemon.start()

    elif args.control == "stop":
        daemon.stop()

    elif args.control == "restart":
        print("Not implemented yet.")


if __name__ == '__main__':
    main()
