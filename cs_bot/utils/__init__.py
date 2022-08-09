from itertools import islice
import urllib.parse
import yaml
import datetime


def read_yaml(path: str):
    """Защищенное чтение yaml"""
    with open(path, 'r') as c:
        return yaml.safe_load(c)


def bild_href(name: str) -> str:
    """создаем href"""
    name = urllib.parse.quote(name)
    ss = f'https://steamcommunity.com/market/listings/730/{name}'
    return ss


def hash_in_name(href: str) -> str:
    return urllib.parse.unquote(href)


def time_block() -> float:
    """Процент, от времени торговли"""
    time_now = datetime.datetime.now()
    beginning = time_now.replace(hour=7, minute=0, second=0, microsecond=0)
    end = time_now.replace(hour=19, minute=0, second=0, microsecond=0)
    if beginning < time_now < end:
        return 0.04
    else:
        return 0.02


def chunks(data: list, size: int):
    """Разделения списка на части"""
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k for k in islice(it, size)}
