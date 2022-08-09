from pydantic import BaseModel


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
