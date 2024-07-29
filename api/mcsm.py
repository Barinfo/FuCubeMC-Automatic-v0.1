import requests
from until import Logger

logger = Logger()


def create_user(url, apikey, username, password, permission=1):
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
    api_url = url + "/api/auth?apikey=" + apikey
    data = {
        'username': username,
        'password': password,
        'permission': permission,
        'apikey': apikey
    }
    headers = {
        'x-requested-with': 'xmlhttprequest'
    }

    try:
        response = requests.post(api_url, data=data, headers=headers)
        logger.debug(response.text)
        if response.status_code == 200:
            return response.json()["data"]["uuid"]
        else:
            logger.error(
                f"Failed to create user. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception occurred in Mcsm Create User: {e}")
        return False


def update_permission(url, apikey, uuid, permission):
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
    api_url = url + "/api/auth?apikey=" + apikey
    data = {
        'username': uuid,
        'password': password,
        'permission': permission,
        'apikey': apikey
    }
    headers = {
        'x-requested-with': 'xmlhttprequest'
    }

    try:
        response = requests.post(api_url, data=data, headers=headers)
        logger.debug(response.text)
        if response.status_code == 200:
            return response.json()["data"]["uuid"]
        else:
            logger.error(
                f"Failed to create user. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception occurred in Mcsm Create User: {e}")
        return False
