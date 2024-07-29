import bcrypt
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from datetime import datetime
import secrets
import random
import ujson as json
import os
from DBUtils.PooledDB import PooledDB
import sqlite3
import threading
import mcsm
from logger import Logger



logger = Logger()

app = Flask(__name__)


with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)

class DBConnection:
    _lock = threading.Lock()
    _pool = None

    def __init__(self):
        if DBConnection._pool is None:
            with DBConnection._lock:
                if DBConnection._pool is None:
                    DBConnection._pool = PooledDB(
                        creator=sqlite3,
                        maxusage=None,
                        maxconnections=5,
                        blocking=True,
                        setsession=[],
                        ping=0,
                        closeable=False,
                        threadlocal=None,
                        database='users.db',
                        check_same_thread=False
                    )
        self.conn = DBConnection._pool.connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


with DBConnection() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            ban TEXT DEFAULT 'false',
            points INTEGER DEFAULT 0,
            last_sign TIMESTAMP,
            token TEXT
        );
    ''')


@app.route('/reg', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if not username or not password:
        return jsonify({'error': '缺少用户名或密码'}), 400

    with DBConnection() as cursor:
        if cursor.execute('SELECT username FROM users WHERE username=?', (username,)).fetchone():
            return jsonify({'error': '用户名已被占用'}), 400
        uuid = mcsm.create_user(config['mcsm']['url'], config['mcsm']['apikey'], username, password)
        if uuid:
          cursor.execute(
            'INSERT INTO users (username, password, uuid) VALUES (?, ?)', (username, hashed_password, uuid))
          logger.info(f"用户 {username} 执行注册成功")
          return jsonify({'message': '注册成功'}), 201
        else:
          return jsonify({'error': uuid}), 500


@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if not username or not password:
        return jsonify({'error': '缺少用户名或密码'}), 400

    with DBConnection() as cursor:
        user = cursor.execute(
            'SELECT points FROM users WHERE username=? AND password=?', (username, hashed_password)).fetchone()
        if user:
            token = secrets.token_hex(16)
            cursor.execute(
                'UPDATE users SET token=? WHERE username=?', (token, username))
            logger.info(f"用户 {username} 执行登录成功")
            return jsonify({'message': '登录成功', 'points': user[0], 'token': token}), 200
        else:
            return jsonify({'error': '账号或密码错误'}), 401


@app.route('/sign', methods=['POST'])
def check_in():
    data = request.json
    username = data.get('username')
    token = data.get('token')
    if username and token:
        with DBConnection() as cursor:
            user = cursor.execute(
                'SELECT last_sign, points, token, ban FROM users WHERE username=?', (username,)).fetchone()
            if user:
                db_token, points, ban = user[2], user[1], user[3]
                if db_token != token:
                    return jsonify({'error': '身份验证失败'}), 401

                if ban == 'true':
                    return jsonify({'error': '你已被封禁'}), 403

                today = datetime.now().date()
                if user[0] and datetime.strptime(user[0], '%Y-%m-%d %H:%M:%S').date() == today:
                    return jsonify({'error': '你已经签到过了！'}), 400

                first = int(config['sign_point']['min'])
                last = int(config['sign_point']['max'])
                pp = random.randint(first, last)

                cursor.execute('UPDATE users SET last_sign=?, points=? WHERE username=?',
                               (datetime.now(), points + pp, username))
                logger.info(f"用户 {username} 执行签到操作，获取积分 {pp}")
                return jsonify({'message': '签到成功', 'points': points + pp}), 200
            else:
                return jsonify({'error': '用户不存在'}), 404
    else:
        return jsonify({'error': '缺少传参'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config["port"], threaded=True)