import os
import ujson as json
import requests

url = "http://s1.rancloud.xyz:23333"

key = "04a1d0c4518e46b7a07622fd32433853"


def addExample(name, type):
    """
    创建实例并返回是否成功的布尔值。

    参数:
    url: API的基础URL
    apikey: API密钥
    name: 实例名
    type: 实例类型(使用minecraft/?)

    返回:
    str: 实例的UUID
    """
    api_url = f"{url}/api/instance?demonId=bf812a47a8e24e738cd36c617727a2b6&apikey={key}"
    DockerConfig = {
        "containerName": "test",
        "image": "openjdk:21",
        "memory": 1024,
        "ports": ["25565:25565/tcp"],
        "extraVolumes": [],
        "maxSpace": None,
        "network": None,
        "io": None,
        "networkMode": "bridge",
        "networkAliases": [],
        "cpusetCpus": "1",
        "cpuUsage": 100,
        "workingDir": "",
        "env": []
    }
    InstanceConfig = {
        "nickname": "New Name",
        "startCommand": "cmd.exe",
        "stopCommand":  "^C",
        "cwd": "/workspaces/my_server/",
        "ie": "gbk",
        "oe": "gbk",
        "createDatetime": "2022/2/3",
        "lastDatetime": "2022/2/3 16:02",
        "type": "universal",
        "tag": [],
        "endTime": "2022/2/28",
        "fileCode": "gbk",
        "processType": "docker",
        "updateCommand": "shutdown -s",
        "actionCommandList": [],
        "crlf": 2,
        "docker": DockerConfig,

        "enableRcon": 'true',
        "rconPassword": "123456",
        "rconPort": 2557,
        "rconIp": "192.168.1.233",

        "terminalOption": {
            "haveColor": 'false',
            "pty": 'true',
        },
        "eventTask": {
            "autoStart": 'false',
            "autoRestart": 'true',
            "ignore": 'false',
        },
        "pingConfig": {
            "ip": "",
            "port": 25565,
            "type": 1,
        }
    }
    data = {
        "config": InstanceConfig,
            "info": {
                "currentPlayers": -1,
                "fileLock": 0,
                "maxPlayers": -1,
                "openFrpStatus": 'false',
                "playersChart": [],
                "version": "",
            },
            "instanceUuid": "50c73059001b436fa85c0d8221c157cf",
            "processInfo": {
                "cpu": 0,
                "memory": 0,
                "ppid": 0,
                "pid": 0,
                "ctime": 0,
                "elapsed": 0,
                "timestamp": 0
            },
            "space": 0,
            "started": 6,
            "status": 3,
    }
    print(str(data).replace("'","\""))
    response = requests.post(api_url, data=data, headers={
        'X-Requested-With': 'XMLHttpRequest'
    })
    print(response.text)
    return response.json()["data"]


print(addExample("test_name", "universal"))
