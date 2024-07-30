from functools import wraps
from flask import request, jsonify
from until import DBConnection

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.cookies.get('auth_token')
        if not auth_token:
            return jsonify({'error': '未授权，请先登录'}), 401
        
        with DBConnection() as cursor:
            user = cursor.execute(
                'SELECT email FROM users WHERE token=?', (auth_token,)).fetchone()
            if user is None:
                return jsonify({'error': '无效的token'}), 401
            request.user = {'email': user[0]}
        
        return f(*args, **kwargs)
    
    return decorated_function