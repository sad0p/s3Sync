import os
import sys
import time
import config
import ctypes
import signal
import s3logger
import s3sync
import s3push


class S3Daemon():
    def __init__(self, config):
        self.INTERVAL = 10.0
        self.pid_file = os.path.join(config.db_location, 's3daemon.pid')
        self.logger = s3logger.create_logger(config.daemon_log_path)
        self.config_obj = config

    def start(self):
        if self.is_running() is True:
            self.logger.warning(
                f"Daemon is running. Pidfile ({self.pid_file}) present.")
            sys.exit(1)

        if ctypes.CDLL(None).daemon(0, 0) < 0:
            self.logger.warning(f"Failed to daemonize")
            sys.exit(1)

        self.pid = os.getpid()
        with open(self.pid_file, 'w') as self.fh:
            self.fh.write(f'{self.pid}')
        self.logger.info("started daemonization")
        self.run()

    def stop(self):
        if self.is_running() is False:
            self.logger.warning(
             f"Daemon is not running. Pidfile ({self.pid_file}) not present")
            sys.exit(1)

        with open(self.pid_file, 'r') as self.fh:
            self.pid = int(self.fh.read())

        self.logger.info(
            f"Terminating daemon with pid {self.pid} in {self.pid_file}")

        os.kill(self.pid, signal.SIGTERM)
        os.remove(self.pid_file)

    def is_running(self):
        return os.path.isfile(self.pid_file)

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
