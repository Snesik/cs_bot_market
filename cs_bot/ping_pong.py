import time

from cs_bot.api_cs.api import RequestsCS


def send_ping():
    auto_ping_pong = RequestsCS()
    response = auto_ping_pong.ping_pong()
    if response:
        time.sleep(120)
    else:
        print('что то не так')
        send_ping()


if __name__ == "__main__":
    while True:
        try:
            send_ping()
        except Exception as error:
            time.sleep(60)