from until import Logger, AccountVerification, DBConnection, Mcsm
from config import config


logger=Logger()
mcsm = Mcsm(config["mcsm"]["url"], config["mcsm"]["apikey"], logger)

print(mcsm.giveExample(user='36f83ef4a03e4c62a232778fb54a0878',Example=None))