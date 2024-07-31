from until import Logger,Mcsm
import os
import json


logger=Logger()
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)
mcsm = Mcsm(config["mcsm"]["url"], config["mcsm"]["apikey"], logger)
mcsm.addExample("0001","")
