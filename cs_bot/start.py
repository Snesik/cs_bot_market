import multiprocessing
import time

from sell_market import start_sell_market
from ping_pong import start_ping
from configrm_trade import start_confirm


#def start():



if __name__ == '__main__':
    p1 = multiprocessing.Process(target=start_ping, daemon=True)

    p2 = multiprocessing.Process(target=start_sell_market, daemon=True)

    p3 = multiprocessing.Process(target=start_confirm, daemon=True)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
