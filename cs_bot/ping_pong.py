import time

from api_cs.api_cs_market import RequestsCS


def send_ping():
    auto_ping_pong = RequestsCS()
    response = auto_ping_pong.ping_pong()
    if response:
        print('Сплю')
        time.sleep(5)
    else:
        print('что то не так')
        send_ping()


if __name__ == "__main__":
    while True:
        send_ping()
