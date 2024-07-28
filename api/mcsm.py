def create_user(url, apikey, username, password, permission=1):
    # 创建用户
    # 返回类型：bool
    # 返回内容解释：True（成功）

    # 参数说明：
    # username: 用户名
    # password: 密码
    # permission: -1（封禁）；1（普通权限）；10（最高权限）

    api_url = url + "/api/overview/setting"

    _body = {
        'username': username, 
        'password': password, 
        'permission': permission, 
    }

    response = sendRequest(api_url, apikey, method="post", body=_body)

    return True