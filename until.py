import datetime
import logging
from datetime import datetime
from typing import Union
import ujson as json
import threading
import os
import uuid
import sqlite3
import re
import requests


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
    def __init__(self, log_file_prefix=os.path.join(os.path.dirname(__file__), 'logs')):
        os.makedirs(log_file_prefix, exist_ok=True)
        self.log_file_prefix = log_file_prefix
        self.logger = logging.getLogger("Custom Logger")
        self.logger.setLevel(logging.DEBUG)

        # 创建控制台输出的handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARN)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 初始化文件handler为None，以便在首次记录日志时创建
        self.file_handler = None
        self.current_log_date = None
        self.lock = threading.Lock()

    def _ensure_log_file_created(self):
        """确保日志文件在首次记录日志时创建，或在新的一天开始时创建新文件。"""
        today = datetime.datetime.now().date()
        if self.file_handler is None or today != self.current_log_date:
            with self.lock:
                if self.file_handler is not None and today != self.current_log_date:
                    self.logger.removeHandler(self.file_handler)
                    self.file_handler.close()

                self.current_log_date = today
                self.log_file = os.path.join(
                    self.log_file_prefix, f"{today}.log")
                self.file_handler = logging.FileHandler(self.log_file)
                self.file_handler.setLevel(logging.DEBUG)
                self.file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
                self.logger.addHandler(self.file_handler)

    def debug(self, message: str) -> None:
        self._ensure_log_file_created()
        with self.lock:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        self._ensure_log_file_created()
        with self.lock:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        self._ensure_log_file_created()
        with self.lock:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        self._ensure_log_file_created()
        with self.lock:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        self._ensure_log_file_created()
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


class Mcsm:
    def __init__(self, url, apikey, logger) -> None:
        self.logger = logger
        self.url = url
        self.apikey = apikey

    def create_user(self, username, password, permission=1):
        """
        创建用户并返回是否成功的布尔值。

        参数:
        url: API的基础URL
        apikey: API密钥
        username: 用户名
        password: 密码
        permission: 用户权限，默认为1（普通权限）

        返回:
        bool: 用户是否成功创建（True表示成功，False表示失败）
        """
        api_url = f"{self.url}/api/auth?apikey={self.apikey}"
        data = {
            'username': username,
            'password': password,
            'permission': permission,
        }
        headers = {
            'x-requested-with': 'xmlhttprequest'
        }

        try:
            response = requests.post(api_url, data=data, headers=headers)
            if response.status_code == 200:
                return response.json()["data"]["uuid"]
            else:
                self.logger.error(
                    f"Failed to create user. Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Exception occurred in Mcsm Create User: {e}")
            return False

    def update_permission(self, uuid: str, permission=int):
        """
        更新用户的权限并返回是否成功的布尔值。

        参数:
        url: API的基础URL
        apikey: API密钥
        uuid: 用户的UUID
        permission: 用户的新权限

        返回:
        bool: 用户权限是否成功更新（True表示成功，False表示失败）
        """
        api_url = f"{self.url}/api/auth?apikey={self.apikey}"
        data = {
            'uuid': uuid,
            'config': {
                'permission': permission
            }
        }
        response = requests.put(api_url, data=data, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        redata = json.loads(response.text)
        return redata["data"]
