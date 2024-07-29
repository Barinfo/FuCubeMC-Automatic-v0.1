


@app.route('/api/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    verification_code = data.get('verificationCode')

    # 验证数据
    if not all([username, email, password, confirm_password, verification_code]):
        return jsonify({'error': 'Missing required fields'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # 验证验证码
    if not verify_code(email, verification_code):
        return jsonify({'error': 'Invalid verification code'}), 400

    # 在这里添加保存用户到数据库的逻辑
    # 例如：
    # user = User(username=username, email=email, password=generate_password_hash(password))
    # db.session.add(user)
    # db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/api/send_verification_code', methods=['GET'])
def send_verification_code():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # 生成验证码
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # 保存验证码到 session 或数据库
    # 例如：
    # session['verification_code'] = verification_code

    # 构建邮件内容
    msg = Message('Verification Code', sender='jackcsa@outlook.com', recipients=[email])
    msg.body = f'Your verification code is: {verification_code}'

    # 发送邮件
    mail.send(msg)

    return jsonify({'message': 'Verification code sent successfully'}), 200


def verify_code(email, code):
    # 在这里验证从 session 或数据库获取的验证码
    # 例如：
    # stored_code = session.get('verification_code')
    # return stored_code == code
    pass

if __name__ == '__main__':
    app.run(debug=True)