import logging
from datetime import datetime
import threading

class Logger:
    def __init__(self, log_file_prefix='logs/'):
        self.log_file = f"{log_file_prefix}{datetime.now().strftime('%Y-%m-%d')}.log"
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # 设置全局日志级别为INFO

        # 创建一个控制台输出的handler，并设置级别为INFO
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARN)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 创建一个文件输出的handler，并设置级别为DEBUG（记录所有级别）
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 添加线程锁
        self.lock = threading.Lock()

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