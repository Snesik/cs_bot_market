from pydantic import BaseModel
from typing import List


class Inventory(BaseModel):
    id: str
    classid: str
    instanceid: str
    market_hash_name: str
    market_price: float
    tradable: int

    def __str__(self):
        return self.market_hash_name


class Items(BaseModel):
    market_hash_name: str
    volume: str
    price: str

    def __str__(self):
        return self.market_hash_name


class Model(BaseModel):
    inventory: Inventory


class Item(BaseModel):
    appid: int
    contextid: int
    assetid: str
    amount: int


class CreatOfferts(BaseModel):
    """Класс создания трейда"""
    hash: str
    partner: int
    token: str
    tradeoffermessage: str
    items: List[Item]
    created: bool
