import requests
import time


timeout=1
while True:
    Time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        response=requests.get('http://s1.rancloud.xyz:24444',timeout=timeout)
        print(Time+"守护进程正常")
    except:
        print(Time+"守护进程下线!")

    try:
        response=requests.get('http://s1.rancloud.xyz:23333',timeout=timeout)
        print(Time+"网页进程正常")
    except:
        print(Time+"网页进程下线!")

    time.sleep(10)