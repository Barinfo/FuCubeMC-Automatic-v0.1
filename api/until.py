import logging
from datetime import datetime
from typing import Union
import threading
import os
import uuid
import sqlite3
import re


def is_email(email: str) -> bool:
    e = r'^[\w.-]+@(' \
        r'qq\.com|' \
        r'126\.com|' \
        r'163\.com|' \
        r'yeah\.net|' \
        r'outlook\.com|' \
        r'139\.com|' \
        r'189\.com' \
        r')$'
    return bool(re.match(e, email))


class DBConnection:
    _lock = threading.Lock()
    _connection = None

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with cls._lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(DBConnection, cls).__new__(cls)
                    cls._instance.conn = sqlite3.connect(
                        os.path.join(os.path.dirname(__file__), 'users.db'))
                    cls._instance.conn.row_factory = sqlite3.Row
        return cls._instance

    def get_cursor(self):
        return self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self.get_cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()


class Logger:
    def __init__(self, log_file_prefix=os.path.join(os.path.dirname(__file__), 'logs')) -> None:
        os.makedirs(log_file_prefix, exist_ok=True)
        self.log_file = os.path.join(
            log_file_prefix, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        self.logger = logging.getLogger("Custom Logger")
        self.logger.setLevel(logging.DEBUG)
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

    def debug(self, message: str) -> None:
        with self.lock:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        with self.lock:
            self.logger.info(message)

    def warnin(self, message: str) -> None:
        with self.lock:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        with self.lock:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        with self.lock:
            self.logger.critical(message)


class AccountVerification:
    def __init__(self) -> None:
        """初始化AccountVerification类，建立数据库连接。"""
        self.db = DBConnection()
        with self.db as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS account_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    verification_id TEXT NOT NULL,
                    verified INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def apply_verification_id(self, email: str) -> str:
        """
        为指定的邮箱申请验证ID。

        参数:
            email (str): 用户邮箱。

        返回:
            str: 生成的验证ID。
        """
        verification_id = str(uuid.uuid4())
        with self.db as cursor:
            cursor.execute(
                "INSERT INTO account_verifications (email, verification_id) VALUES (?, ?, ?)",
                (email, verification_id)
            )
        return verification_id

    def verify_id(self, verification_id: str) -> bool:
        """
        验证给定的ID并更新数据库。

        参数:
            verification_id (str): 待验证的ID。

        返回:
            bool: 如果更新成功则返回True，否则False。
        """
        with self.db as cursor:
            cursor.execute(
                "UPDATE account_verifications SET verified = 1 WHERE verification_id = ?",
                (verification_id,)
            )
        return cursor.rowcount > 0

    def is_verified(self, identifier: Union[str, int]) -> bool:
        """
        检查给定的邮箱是否已验证。

        参数:
            identifier (Union[str, int]): 邮箱。

        返回:
            bool: 如果已验证则返回True，否则False。
        """
        with self.db as cursor:
            cursor.execute(
                "SELECT verified FROM account_verifications WHERE email = ?",
                (identifier,)
            )
            result = cursor.fetchone()
        return result and result['verified'] == 1

    def get_email(self, vid: Union[str, int]) -> str:
        """
        获取给定的vid的邮箱

        参数:
            vid (Union[str, int]): 验证id

        返回:
            str: 邮箱
        """
        with self.db as cursor:
            cursor.execute(
                "SELECT email FROM account_verifications WHERE verification_id = ?",
                (vid,)
            )
            result = cursor.fetchone()
        return result['email']
