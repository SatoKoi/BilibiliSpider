import logging
import sys


class Logger(object):
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s \tby - %(name)s")

    def __init__(self, name="log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

    def add_stream_handler(self):
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(self.formatter)
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

    def add_file_handler(self, file='log.log', level=logging.INFO):
        file_handler = logging.FileHandler(file, encoding='utf8')
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)