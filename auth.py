from datetime import datetime
from until import DBConnection

def is_token_valid(token):
    """
    检查给定的令牌是否有效。
    
    参数:
    token (str): 要验证的令牌字符串。

    返回:
    bool: 如果令牌有效则返回True，否则返回False。
    """
    with DBConnection() as cursor:
        query = """
            SELECT logtime, username 
            FROM users 
            WHERE token = ?
        """
        cursor.execute(query, (token,))
        row = cursor.fetchone()
        if not row:
            return False
        logtime = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        time_diff = (current_time - logtime).total_seconds()
        if time_diff < 60 * 30 or row[1]:   # 有效期30分钟
            return True
        else:
            return False