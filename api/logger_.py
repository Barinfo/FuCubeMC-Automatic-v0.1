import logging
from datetime import datetime
import threading
import os


class Logger_:
    def __init__(self, log_file_prefix=os.path.join(os.path.dirname(__file__), 'logs')):
        os.makedirs(log_file_prefix, exist_ok=True)
        self.log_file = os.path.join(
            log_file_prefix, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        self.logger = logging.getLogger("Custom Logger")
        self.logger.setLevel(logging.INFO)
        # 创建一个控制台输出的handler，并设置级别为WARN
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARN)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 创建一个文件输出的handler，并设置级别为DEBUG（记录所有级别）
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 添加线程锁
        self.lock = threading.Lock()

    def debug(self, message):
        with self.lock:
            self.logger.debug(message)

    def info(self, message):
        with self.lock:
            self.logger.info(message)

    def warning(self, message):
        with self.lock:
            self.logger.warning(message)

    def error(self, message):
        with self.lock:
            self.logger.error(message)

    def critical(self, message):
        with self.lock:
            self.logger.critical(message)
