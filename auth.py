from datetime import datetime
from until import DBConnection
from flask import request, make_response, jsonify
from config import config
import bcrypt
import ujson as json
import os
import re


class Auth:
    @staticmethod
    def get_id_by_reg_email(email: str) -> str:
        """
        根据用户注册所用email获取用户id

        参数:
        - email (str): 用户注册所用email。

        返回:
        - int: 用户id。
        """
        with DBConnection() as cursor:
            cursor.execute(
                "SELECT id FROM account_verifications WHERE email = ?",
                (email,)
            )
            result = cursor.fetchone()
        return result['id']

    @staticmethod
    def get_name_by_email(email: str) -> str:
        """
        根据用户当前email获取用户name

        参数:
        - email (str): 用户当前email。

        返回:
        - str: 用户username。
        """
        with DBConnection() as cursor:
            cursor.execute(
                "SELECT username FROM users WHERE email = ?", (email,)
            )
            row = cursor.fetchone()
        return row['username']

    @staticmethod
    def get_name_by_id(id: int) -> str:
        """
        根据用户id获取用户name

        参数:
        - id (str): 用户id。

        返回:
        - str: 用户username。
        """
        with DBConnection() as cursor:
            cursor.execute(
                "SELECT username FROM users WHERE id = ?", (id,)
            )
            row = cursor.fetchone()
        return row['username']

    @staticmethod
    def get_info(id: int) -> dict:
        """
        根据用户ID获取用户信息。

        返回字典参数说明

        - id  用户唯一id
        - uuid    用户唯一MCSM uuid
        - email   用户邮箱
        - password    用户密码(密文)
        - role    用户角色
        - points  用户积分
        - sign_count   用户签到次数
        - last_sign    用户上次签到时间

        参数:
        - id (int): 用户ID。

        返回:
        - dict: 用户信息字典。
        """
        with DBConnection() as cursor:
            cursor.execute(
                "SELECT id, uuid, email, password, role, points, sign_count, last_sign FROM users WHERE id = ?", (
                    id,)
            )
            row = cursor.fetchone()
        return row

    @staticmethod
    def is_email(email: str) -> bool:
        """
        检查给定的字符串是否为有效的电子邮件地址。

        参数:
        - email (str): 要检查的电子邮件地址。

        返回:
        - bool: 如果电子邮件地址有效则返回True，否则返回False。
        """
        pattern = r'^[\w.-]+@(qq\.com|126\.com|163\.com|yeah\.net|outlook\.com|139\.com|189\.com)$'
        return bool(re.match(pattern, email))

    @staticmethod
    def load_salt() -> bytes:
        """
        加载或生成盐值。

        返回:
        - bytes: 盐值。
        """
        if 'salt' not in config:
            config['salt'] = bcrypt.gensalt().decode()
            with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as file:
                json.dump(config, file, indent=4)
        return config['salt'].encode('utf-8')

    @staticmethod
    def is_token_valid(token: str, id: str) -> bool:
        """
        检查给定的令牌是否有效。

        参数:
        - token (str): 要验证的令牌字符串。
        - id (str): 要验证的令牌对应的用户ID。

        返回:
        - bool: 如果令牌有效则返回True，否则返回False。
        """
        with DBConnection() as cursor:
            cursor.execute(
                "SELECT logtime, username FROM users WHERE token = ? AND id = ?",
                (token, id)
            )
            row = cursor.fetchone()
            if not row:
                return False
            logtime = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            time_diff = (current_time - logtime).total_seconds()
            if time_diff < 60 * 30:  # 有效期30分钟
                return True
            else:
                return False

    @staticmethod
    def get_token() -> str:
        """
        从请求中获取 token 的函数。
        首先尝试从 cookie 中获取 token，
        如果 cookie 中没有找到 token，则尝试从请求数据中获取。

        返回:
        - str: token 值，如果未找到则返回 None。
        """
        token = request.cookies.get('token')
        if token is None:
            data = request.values.to_dict(flat=True)
            if data:
                token = data.get('token')
        return token

    @staticmethod
    def set_cookies_and_return_body(cookie_dict: dict, body) -> object:
        """
        设置 cookie 并返回响应体。

        参数:
        - cookie_dict (dict): 包含要设置为 cookie 的键值对的字典。
        - body (str or dict): 要作为响应体返回的内容。

        返回:
        - object: 设置了 cookie 并携带响应体的 Flask 响应对象。
        """
        response = make_response(
            jsonify(body) if isinstance(body, dict) else body)
        for key, value in cookie_dict.items():
            response.set_cookie(key, value)
        return response

    def get_hash_password(self, password: str) -> bytes:
        """
        使用 bcrypt 生成密码的哈希值。

        参数:
        - password (str): 明文密码。

        返回:
        - bytes: 密码的哈希值。
        """
        return bcrypt.hashpw(password.encode('utf-8'), self.load_salt())
