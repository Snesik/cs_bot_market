import time

from cs_bot.variables import BOTS
from cs_bot.api_cs.api import RequestsCS


def send_ping(bot):
    auto_ping_pong = RequestsCS(bot)
    response = auto_ping_pong.ping_pong()
    if response:
        time.sleep(120)
    else:
        print('что то не так')
        send_ping(bot)


if __name__ == "__main__":
    while True:
        for BOT in BOTS:
            bot = BOTS[BOT]
            try:
                send_ping(bot)
            except Exception as error:
                time.sleep(30)
