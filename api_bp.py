from flask import request, jsonify, Blueprint
from flask_mail import Message, Mail
from datetime import datetime
from until import Logger, AccountVerification, DBConnection, is_email, Mcsm
import secrets
import random
import ujson as json
import os
import random
import bcrypt


def load_salt():
    if 'salt' not in config:
        config['salt'] = bcrypt.gensalt().decode()

        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as file:
            json.dump(config, file, indent=4)

    return config['salt'].encode('utf-8')



with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)

logger = Logger()
Ver = AccountVerification()
mcsm = Mcsm(config["mcsm"]["url"], config["mcsm"]["apikey"], logger)
mail = Mail()

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/reg', methods=['POST'])
def register_user():
    data = request.args.to_dict()
    password = data.get('password')
    email = data.get('email')

    if not is_email(email):
        return jsonify({'error': '邮箱格式错误'}), 400

    confirm_password = data.get('confirmPassword')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), load_salt())
    if not all([email, password, confirm_password]):
        return jsonify({'error': '缺少传参'}), 400

    if password != confirm_password:
        return jsonify({'error': '两次输入的密码不一样'}), 400

    with DBConnection() as cursor:
        if cursor.execute('SELECT email FROM users WHERE email=?', (email,)).fetchone():
            return jsonify({'error': '邮箱已被注册'}), 400
        uuid = mcsm.create_user(email, password, -1)
        if uuid:
            cursor.execute(
                'INSERT INTO users (email, password, uuid) VALUES (?, ?)', (email, hashed_password, uuid))
            logger.info(f"用户 {email} 执行注册成功")
            vid = Ver.apply_verification_id(email)
            msg = Message('【FuCube】注册激活',
                          sender='FuCube@com.cn', recipients=[email])
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
            return jsonify({'error': uuid}), 500


@api_bp.route('/login', methods=['POST'])
def login_user():
    data = request.args.to_dict()
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), load_salt())
    if not email or not password:
        return jsonify({'error': '缺少用户名或密码'}), 400

    with DBConnection() as cursor:
        user = cursor.execute(
            'SELECT points FROM users WHERE email=? AND password=?', (email, hashed_password)).fetchone()
        if user:
            if not Ver.is_verified(email):
                return jsonify({'error': '账号未激活'}), 401
            token = secrets.token_hex(16)
            cursor.execute(
                'UPDATE users SET token=? WHERE email=?', (token, email))
            logger.info(f"用户 {email} 执行登录成功")
            return jsonify({'message': '登录成功', 'points': user[0], 'token': token}), 200
        else:
            return jsonify({'error': '账号或密码错误'}), 401


@api_bp.route('/sign', methods=['POST'])
def check_in():
    data = request.args.to_dict()
    email = data.get('email')
    token = data.get('token')
    if email and token:
        with DBConnection() as cursor:
            user = cursor.execute(
                'SELECT last_sign, points, token, ban FROM users WHERE email=?', (email,)).fetchone()
            if user:
                if not Ver.is_verified(email):
                    return jsonify({'error': '账号未激活'}), 401
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

                cursor.execute('UPDATE users SET last_sign=?, points=? WHERE email=?',
                               (datetime.now(), points + pp, email))
                logger.info(f"用户 {email} 执行签到操作，获取积分 {pp}")
                return jsonify({'message': '签到成功', 'points': points + pp, 'add': pp}), 200
            else:
                return jsonify({'error': '用户不存在'}), 404
    else:
        return jsonify({'error': '缺少传参'}), 400
