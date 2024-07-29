import bcrypt
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from datetime import datetime
import secrets
import random
import ujson as json
import os
import sqlite3
import threading
import mcsm
from logger_ import Logger_
import random
import re

app = Flask(__name__)

logger_ = Logger_()

app.config['MAIL_SERVER'] = 'smtp.yeah.net'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'barinfo@yeah.net'
app.config['MAIL_PASSWORD'] = 'TQCSAJGFEWKOPJGM'
app.config['SECRET_KEY'] = '?'

mail = Mail(app)

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)


def is_email(email):
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
                    cls._instance.conn = sqlite3.connect(os.path.join('api', 'users.db'))
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
        self.conn.commit()
        self.conn.close()


with DBConnection() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            eamil TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            ban TEXT DEFAULT 'false',
            points INTEGER DEFAULT 0,
            last_sign TIMESTAMP,
            token TEXT
        );
    ''')

@app.route('/active', methods=['GET'])
def _():
    id = request.args.get('id')
    pass
    #这里进行链接验证，别动

@app.route('/api/reg', methods=['POST'])
def register_user():
    data = request.form
    password = data.get('password')
    email = data.get('email')

    if not is_email(email):
        return jsonify({'error': '邮箱格式错误'}), 400

    confirm_password = data.get('confirmPassword')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if not all([email, password, confirm_password]):
        return jsonify({'error': '缺少传参'}), 400

    if password != confirm_password:
        return jsonify({'error': '两次输入的密码不一样'}), 400

    with DBConnection() as cursor:
        if cursor.execute('SELECT email FROM users WHERE username=?', (email,)).fetchone():
            return jsonify({'error': '邮箱已被注册'}), 400
        uuid = mcsm.create_user(
            config['mcsm']['url'], config['mcsm']['apikey'], email, password)
        if uuid:
            cursor.execute(
                'INSERT INTO users (username, password, uuid) VALUES (?, ?)', (email, hashed_password, uuid))
            logger_.info(f"用户 {email} 执行注册成功")
            msg = Message('【ShitCloud】注册激活',
                          sender='ShitCloud@com.cn', recipients=[email])
            mail.html = f'''
<table class="main" width="100%" cellpadding="0" cellspacing="0" style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; border-radius: 3px; background-color: #fff; margin: 0; border: 1px 
 solid #e9e9e9;
" bgcolor=" #fff">
    <tbody>
        <tr style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 14px;
margin: 0;
">
            <td class=" alert alert-warning" style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 16px;
vertical-align: top;
color: #fff;
font-weight: 500;
text-align: center;
border-radius: 3px 3px 0 0;
background-color: #009688;
margin: 0;
padding: 20px;
" align=" center" bgcolor=" #FF9F00" valign=" top">激活FuCube账户</td>
        </tr>
        <tr style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 14px;
margin: 0;
">
            <td class=" content-wrap" style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 14px;
vertical-align: top;
margin: 0;
padding: 20px;
" valign=" top">
                <table width=" 100%" cellpadding=" 0" cellspacing=" 0" style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 14px;
margin: 0;
">
                    <tbody>
                        <tr style=" font-family: 'Helvetica Neue',
Helvetica,
Arial,
sans-serif;
box-sizing: border-box;
font-size: 14px;
margin: 0;
">
                            <td class=" content-block" style=" font-family: 'Helvetica 
 Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">亲爱的<strong style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><a href="mailto:{email}" rel="noopener" target="_blank">{email}</a></strong>：</td>
                        </tr>
                        <tr style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
                            <td class="content-block" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">感谢您注册FuCube,请点击下方按钮完成账户激活。</td>
                        </tr>
                        <tr style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
                            <td class="content-block" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top"><a href="https://{{active?id=xxx}}" class="btn-primary" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; color: #FFF; text-decoration: none; line-height: 2em; font-weight: bold; text-align: center; cursor: pointer; display: inline-block; border-radius: 5px; text-transform: capitalize; background-color: #009688; margin: 0; border-color: #009688; border-style: solid; border-width: 10px 20px;" rel="noopener" target="_blank">激活账户</a></td>
                        </tr>
                        <tr style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
                            <td class="content-block" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">感谢您选择FuCube。</td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </tbody>
</table>
            '''
            mail.send(msg)
            return jsonify({'message': '注册成功，请前往邮箱验证'}), 201
        else:
            return jsonify({'error': uuid}), 500


@app.route('/api/login', methods=['POST'])
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
            logger_.info(f"用户 {username} 执行登录成功")
            return jsonify({'message': '登录成功', 'points': user[0], 'token': token}), 200
        else:
            return jsonify({'error': '账号或密码错误'}), 401


@app.route('/api/sign', methods=['POST'])
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
                logger_.info(f"用户 {username} 执行签到操作，获取积分 {pp}")
                return jsonify({'message': '签到成功', 'points': points + pp}), 200
            else:
                return jsonify({'error': '用户不存在'}), 404
    else:
        return jsonify({'error': '缺少传参'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config["port"], threaded=True)
