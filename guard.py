import requests


timeout=1

try:
    response=requests.get('http://s1.rancloud.xyz:24444',timeout=timeout)
    print(response.text)
except:
    print("守护进程下线!")

try:
    response=requests.get('http://s1.rancloud.xyz:23333',timeout=timeout)
    print(response.text)
except:
    print("网页进程下线!")