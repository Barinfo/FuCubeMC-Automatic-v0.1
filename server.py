from flask import Flask, send_from_directory, abort, request, jsonify
from flask_mail import Mail, Message
from datetime import datetime
from until import Logger, AccountVerification, DBConnection, Mcsm
from panel import app as panel_app
from auth import Auth
from config import config
import secrets
import random
import os
import bcrypt

app = Flask(__name__, static_folder='templates')

app.config['MAIL_SERVER'] = 'smtp.yeah.net'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'barinfo@yeah.net'
app.config['MAIL_PASSWORD'] = 'TQCSAJGFEWKOPJGM'
app.config['SECRET_KEY'] = '?'

app.register_blueprint(panel_app, url_prefix='/panel')

mail = Mail(app)

logger = Logger()
Ver = AccountVerification()
Auth = Auth()
mcsm = Mcsm(config["mcsm"]["url"], config["mcsm"]["apikey"], logger)

with DBConnection() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'default',
            points INTEGER DEFAULT 10,
            sign_count INTEGER DEFAULT 0,
            logtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_sign TIMESTAMP,
            token TEXT
        );
    ''')


@app.route('/active', methods=['GET'])
def active_account():
    vid = request.args.to_dict().get('id')
    if Ver.verify_id(vid):
        mcsm.update_permission(mcsm.get_uuid_by_name(
            Auth.get_name_by_email(Ver.get_email(vid))), 1)
        logger.info(f"邮箱 {Ver.get_email(vid)} 执行激活成功")
        return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>验证结果</title>
</head>
<body>
    <h1 style="color:#66ccff;">验证成功，3秒后跳转到登录页面。</h1>
    <script>window.onload(function(){setInterval(function(){window.location.href="https://yun.wh1t3zz.top/login";},3000);});</script>
</body>
</html>'''
    else:
        logger.info(f"邮箱 {Ver.get_email(vid)} 执行激活失败")
        return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>验证结果</title>
</head>
<body>
    <h1>验证失败</h1>
</body>
</html>'''


@app.route('/api/reg', methods=['POST'])
def register_user():
    data = request.values.to_dict(flat=True)
    #logger.debug(data)
    password = data.get('password')
    email = data.get('email')
    username = data.get('username')
    confirm_password = data.get('confirmPassword')
    gRecaptchaResponse = data.get('g-recaptcha-response')
    if not all([email, password, confirm_password, gRecaptchaResponse, username]):
        # 创建一个字典来存储缺失的参数
        missing_params = []
        if username is None:
            missing_params.append('username')
        if email is None:
            missing_params.append('email')
        if password is None:
            missing_params.append('password')
        if confirm_password is None:
            missing_params.append('confirm_password')
        if gRecaptchaResponse is None:
            missing_params.append('g-recaptcha-response')

        # 构造错误消息
        error_message = '缺少以下参数: ' + ', '.join(missing_params)

        # 返回带有详细错误信息的 JSON 响应
        return jsonify({'error': error_message}), 400

    if not Auth.is_email(email):
        return jsonify({'error': '邮箱格式错误'}), 400

    if len(username) > 12 or len(username) < 3:
        return jsonify({'error': '用户名过长或过短'}), 400

    if password != confirm_password:
        return jsonify({'error': '两次输入的密码不一样'}), 400

    hashed_password = Auth.get_hash_password(password)

    with DBConnection() as cursor:
        if cursor.execute('SELECT email FROM users WHERE email=?', (email,)).fetchone():
            return jsonify({'error': '邮箱已被注册'}), 400
    uuid = mcsm.create_user(username, password, -1)
    if uuid[0] == True:
        with DBConnection() as cursor:
            cursor.execute(
                'INSERT INTO users (username, email, password, uuid) VALUES (?, ?, ?, ?)', (username, email, hashed_password, uuid[1]))
        logger.info(f"邮箱 {email} 执行注册成功")
        vid = Ver.apply_verification_id(email)
        msg = Message('【FuCubeMC】注册激活',
                      sender='barinfo@yeah.net', recipients=[email])
        msg.html = f'''
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
                            <td class="content-block" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top"><a href="https://{config["hostname"]}/active?id={vid}" class="btn-primary" style="font-family: ' Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; color: #FFF; text-decoration: none; line-height: 2em; font-weight: bold; text-align: center; cursor: pointer; display: inline-block; border-radius: 5px; text-transform: capitalize; background-color: #009688; margin: 0; border-color: #009688; border-style: solid; border-width: 10px 20px;" rel="noopener" target="_blank">激活账户</a></td>
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
        return jsonify({'message': '注册成功，请前往邮箱验证'}), 200
    else:
        return jsonify({'error': uuid[1]}), 500


@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.args.to_dict()
    username = data.get('username')
    password = data.get('password')
    hashed_password = Auth.get_hashed_password(password)
    if not username or not password:
        return jsonify({'error': '缺少用户名或密码'}), 400

    with DBConnection() as cursor:
        user = cursor.execute(
            'SELECT id, points FROM users WHERE password=? AND username=? OR email=?', (hashed_password, username, username)).fetchone()
        if user:
            if not Ver.is_verified(user['id']):
                return jsonify({'error': '账号未激活'}), 401
            token = secrets.token_hex(16)
            cursor.execute(
                'UPDATE users SET token=?, logtime=? WHERE id=?', (token, datetime.now(), user['id']))
            logger.info(f"用户ID {user['id']} 执行登录成功")
            resp = Auth.set_cookies_and_return_body(
                {'token': token, 'id': user['id']}, {'message': '登录成功', 'points': user['points']})
            return resp, 200
        else:
            return jsonify({'error': '账号或密码错误'}), 401


@app.route('/api/sign', methods=['POST'])
def check_in():
    data = request.args.to_dict()
    id = data.get('id')
    token = Auth.get_token()

    if id and token:
        with DBConnection() as cursor:
            user = cursor.execute(
                'SELECT last_sign, sign_count, points, role FROM users WHERE id=?', (id,)).fetchone()

            if user:
                if not Ver.is_verified(id):
                    return jsonify({'error': '账号未激活'}), 401

                points, role = user['points'], user['role']

                if role == 'ban':
                    return jsonify({'error': '你已被封禁'}), 403

                if Auth.is_token_valid(token, id):
                    return jsonify({'error': '身份验证失败'}), 401

                today = datetime.now().date()
                if datetime.strptime(user['last_sign'], '%Y-%m-%d %H:%M:%S').date() == today:
                    return jsonify({'error': '你已经签到过了！'}), 400

                count = user['sign_count'] + 1
                # 检查是否是初次签到
                if user['sign_count'] == 0:
                    new_points = points + 15
                    cursor.execute('UPDATE users SET last_sign=?, points=?, sign_count=? WHERE id=?',
                                   (datetime.now(), new_points, count, id))
                    logger.info(f"用户ID {id} 执行初次签到操作，获取积分 15")
                    return jsonify({'message': '初次签到成功', 'points': new_points, 'add': 15}), 200

                # 非初次签到的逻辑
                first = int(config['sign_point']['min'])
                last = int(config['sign_point']['max'])
                pp = random.randint(first, last)

                cursor.execute('UPDATE users SET last_sign=?, points=?, sign_count=? WHERE id=?',
                               (datetime.now(), points + pp, count, id))
                logger.info(f"用户ID {id} 执行签到操作，获取积分 {pp}")
                return jsonify({'message': '签到成功', 'points': points + pp, 'add': pp}), 200
            else:
                return jsonify({'error': '用户不存在'}), 404
    else:
        return jsonify({'error': '缺少传参'}), 400


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/reg')
def reg():
    return send_from_directory(app.static_folder, 'reg.html')


@app.route('/login')
def login():
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route('/css/<path:filename>')
def css(filename):
    try:
        return send_from_directory(os.path.join(app.static_folder, "css"), filename)
    except FileNotFoundError:
        abort(404)


@app.route('/js/<path:filename>')
def js(filename):
    try:
        return send_from_directory(os.path.join(app.static_folder, "js"), filename)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config["port"], threaded=True)
