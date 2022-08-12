from variables import STEAM_ID
from utils import bild_href, time_block
from pydantic import BaseModel

# class Inventory:
#     def __init__(self):
#         self.steam_id = STEAM_ID


class SellInfo:
    """Класс предмета из инвентаря, добавляются все действия информация из:
        БД + Sell + Offerts + Количество в наличие
    """

    def __init__(self, name, id, class_id, sell_bd, instanse_id):
        self.name = name
        self.id = [str(id)]
        self.class_id = class_id
        self.sell_bd = sell_bd
        self.instanse_id = instanse_id
        self.href = bild_href(name)
        self.price = 0
        self.low_avg = 0
        self.avg_result = 0
        self.sell_orders = []

    def min_price(self):
        return self.avg_result - (self.avg_result * time_block())

    def range_price(self):
        we_send_price = self.sell_orders[0] - 0.01
        stack = 0
        for i in self.sell_orders:
            if i < we_send_price + 0.10:
                stack += 1
        return stack

    def __str__(self):
        return self.name


class Offert:
    """Передаем 1 экземляр из списка, полученого от API"""

    def __init__(self, data):
        self.id = [asset['assetid'] for asset in data['items']]
        self.partner = data['partner']
        self.message = data['tradeoffermessage']

    def __str__(self):
        return str(self.partner)

