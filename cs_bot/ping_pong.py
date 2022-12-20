import time

from cs_bot.variables import BOTS
from cs_bot.api_cs.api import RequestsCS


def send_ping(bot):
    auto_ping_pong = RequestsCS(bot)
    response = auto_ping_pong.ping_pong()
    if response:
        #time.sleep(60)
        return
    else:
        print('что то не так')
        time.sleep(15)
        send_ping(bot)


def start_ping():
    while True:
        for BOT in BOTS:
            bot = BOTS[BOT]
            try:
                send_ping(bot)
            except Exception as error:
                pass
                #time.sleep(30)
        time.sleep(100)