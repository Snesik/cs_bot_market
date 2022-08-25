from utils import bild_href, time_block
from pydantic import BaseModel
from pydantic.schema import Optional
from typing import List


class SellInfo:
    """Класс предмета из инвентаря, добавляются все действия информация из:
        БД + Sell + Offerts + Количество в наличие
    """

    def __init__(self, name, id, class_id, sell_bd, instanse_id):
        self.hash_name = name
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
        """Прайм тайм продаж"""
        return self.avg_result - (self.avg_result * time_block())

    def range_price(self):
        """Расчет стака цен на предмет"""
        we_send_price = self.sell_orders[0] - 0.01
        stack = 0
        for i in self.sell_orders:
            if i < we_send_price + 0.10:
                stack += 1
        return stack

    def __repr__(self):
        return f'name: {self.hash_name} id: {len(self.id)} '


class Item(BaseModel):
    """Предметы для передачи получаем с КС маркета"""
    appid: int
    contextid: int
    assetid: str
    amount: int


class Offer(BaseModel):
    """Оферты получаем с КС маркета"""
    hash: str
    partner: int
    token: str
    tradeoffermessage: Optional = str
    items: List[Item]
    created: Optional = bool


class ItemsConfirm(BaseModel):
    """Класс для работы с подтверждением, получаем с КС маркета"""
    success: bool
    offers: List[Offer]


class ItemSteamConfirm(BaseModel):
    """Класс для работы с подтверждением, получаем с STEAM из аутентификатора"""
    data_confid: str
    data_key: str
    name: str
    data_accept: str
    id: str



