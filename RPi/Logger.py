import os.path
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    NOTHING = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    OK = 4
    LOG = 5

class Logger(object):
    log_names = ["NOTHING", "ERROR", "WARNING", "INFO", "OK", "LOG"]
    log_colors = ["", '\033[91m', '\033[93m', '\033[94m', "\033[92m", ""]
    log_color_end = "\033[0m"

    def __init__(self, log_file, log_level=LogLevel.LOG, console_log_level=LogLevel.WARNING, console_colors=False, file_colors=False):
        if log_file is not None:
            if not os.path.isfile(log_file):
                print("Could not find file " + log_file + ". Creating\n")
                with open(log_file, "w") as write_file:
                    write_file.write("")
            else:
                with open(log_file, "a") as write_file:
                    write_file.write("\n")
        self.log_file = log_file
        self.log_level = log_level
        self.console_log_level = console_log_level
        self.console_colors = console_colors
        self.file_colors = file_colors

    def log(self, msg, log_level=LogLevel.LOG):
        msg = str(msg)
        log_ = "[" + datetime.now().strftime("%Y:%M:%d %H:%M:%S") + " " + self.log_names[log_level.value] + "]: " + msg
        col_log = self.log_colors[log_level.value] + log_ + self.log_color_end
        if log_level.value <= self.console_log_level.value:
            print col_log if self.console_colors else log_
        if log_level.value <= self.log_level.value:
            if self.log_file is not None:
                with open(self.log_file, "a") as write_file:
                    write_file.write((col_log if self.file_colors else log_) + "\n")

    def error(self, msg):
        self.log_error(msg)

    def log_error(self, msg):
        self.log(msg, LogLevel.ERROR)

    def warning(self, msg):
        self.log_warning(msg)

    def log_warning(self, msg):
        self.log(msg, LogLevel.WARNING)

    def info(self, msg):
        self.log_info(msg)

    def log_info(self, msg):
        self.log(msg, LogLevel.INFO)

    def ok(self, msg):
        self.log_ok(msg)

    def log_ok(self, msg):
        self.log(msg, LogLevel.OK)


if __name__ == "__main__":
    log = Logger("log.txt", LogLevel.LOG, LogLevel.WARNING, True)
    log.log("Hallo", LogLevel.ERROR)
    log.log("Hallo", LogLevel.WARNING)
    log.log("Hallo", LogLevel.INFO)
    log.log("Hallo", LogLevel.OK)
    log.log("Hallo")

