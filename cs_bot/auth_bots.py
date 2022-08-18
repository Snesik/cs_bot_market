import re
import requests
import pickle
import requests.cookies
import os
import time
from urllib3.util.retry import Retry
from steampy.login import LoginExecutor
from collections import defaultdict

bots = defaultdict(list)

head = {'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

path = os.path.abspath('')
# path = os.path.abspath('Bot/cookes/')
session = {}


def create_session_id_cookie(name: str, value: str) -> dict:
    return {"name": f"{name}",
            "value": value,
            "domain": SteamUrl.COMMUNITY_URL[8:]}


"""Список ботов"""


class SteamUrl:
    COMMUNITY_URL = "https://steamcommunity.com"
    STORE_URL = 'https://store.steampowered.com'


def take_info_bots(path):
    with open(path + '/cookes/setting.txt') as f:
        global add_cookies_file
        add_cookies_file = 0
        """Словарь, ключ имя бота внутри листы, 0 = пароль, 1 = шаракей, 2 = steamID"""
        need_only_cancel = 0
        bots_txt = [i for i in f.read().split() if i[0] != '#']
    for i in bots_txt:
        """Сохранять или нет новые куки"""
        if i == "add_cookies_file=0":
            continue
        elif i == "add_cookies_file=1":
            add_cookies_file = 1
            continue

        bot = str.split(i, ',')
        if '!' in bot[0]:
            bot[0] = re.sub('!', '', bot[0])
            need_only_cancel = 1
        bots[f'{bot[0]}'].append(bot[1])
        bots[f'{bot[0]}'].append(bot[2])
        bots[f'{bot[0]}'].append(bot[3])
        bots[f'{bot[0]}'].append(bot[4])
        bots[f'{bot[0]}'].append(bot[5])
        bots[f'{bot[0]}'].append(need_only_cancel)

    return bots




from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 10  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    """Авто подстановка timeout в сессию"""

    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        try:
            return super().send(request, **kwargs)
        except Exception as error:
            time.sleep(6)
            return super().send(request, **kwargs)


"""Настройка сессии ботов"""


def creation_session_bots(path=path):
    bots = take_info_bots(path)
    for bot in bots:
        """Сессия, по имени бота"""
        session[bot] = requests.Session()

        username = bot
        password = bots[bot][0]
        steam_guard = bots[bot][1]
        steam_id = bots[bot][2]

        if add_cookies_file == 1:
            LoginExecutor(username, password, steam_guard, session[bot]).login()
            dump_cookies(session[bot], f'{bot}')
        elif add_cookies_file == 0:
            load_cookies(session[bot], f'{bot}')

        retries = Retry(total=10, backoff_factor=1)
        session[bot].mount('http://', TimeoutHTTPAdapter(max_retries=retries))
        session[bot].mount('https://', TimeoutHTTPAdapter(max_retries=retries))

        session[bot].headers.update(head)
        session[bot].get("https://steamcommunity.com")
        session[bot].cookies.set(
            **create_session_id_cookie('steamRememberLogin', session[bot].cookies['steamRememberLogin']))

        print(f'Сессия создана для {bot}')
    return session


def dump_cookies(session, filename):
    cookies = []
    for c in session.cookies:
        cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "expires": c.expires
        })
    with open(path + '\cookes\\' + filename, 'wb') as f:
        pickle.dump(cookies, f)


def load_cookies(session, filename, ):
    with open(path + '/cookes/' + filename, 'rb') as f:
        cookies = pickle.load(f)
    for c in cookies:
        session.cookies.set(**c)


if __name__ == '__main__':
    creation_session_bots()
    # for i in bots:
    #     ConfirmationExecutor('2JOCO3DHK7AkNZbLF\/ArOuvOByk=', bots[i][2], session[i]).confirm_sell_listing()
    # ConfirmationExecutor._get_confirmation_sell_listing_id()
