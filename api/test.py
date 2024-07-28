import mcsm
import os
import json


#测试用

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)
mcsm.create_user(url=config['mcsm']['url'], apikey=config['mcsm']['apikey'], 
        username='123', password='123123123123Aa')