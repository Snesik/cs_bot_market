from typing import List, Any

import requests
from cs_bot.variables import API_CS_KEY, API_STEAM_KEY
from cs_bot.api_cs.models import Inventory, Items, CreatOfferts


class RequestsCS:
    """Класс API CS market"""
    v1 = 'https://market.csgo.com/api'
    v2 = 'https://market.csgo.com/api/v2'

    def __init__(self):
        self._cs_api = API_CS_KEY
        self._steam_api = API_STEAM_KEY

    """Запросы через api"""

    def my_inventory(self) -> list:
        """Предметы для продажи в моем инвентаре"""
        response = requests.get(f'{self.v2}/my-inventory/?key={self._cs_api}').json()
        if response['success']:
            return [Inventory(**i) for i in response['items']]
        raise f'ОШИБКА {response}'

    def all_price(self) -> list:
        """Цены на все товары"""
        response = requests.get(f'{self.v2}/prices/RUB.json').json()
        if response['success']:
            return [Items(**i) for i in response['items']]
        raise f'ОШИБКА {response}'

    def all_sell(self):
        """Выставленные на продажу лоты"""
        return requests.get(f'{self.v2}/items?key={self._cs_api}').json()

    def update_inv(self):
        """Обновить информацию об инвентаре, рекомендация проводить после каждой передачи предмета"""
        return requests.get(f'{self.v2}/update-inventory/?key={self._cs_api}').json()

    def test(self):
        """Проверить возможность работы, все должны быть TRUE"""
        return requests.get(f'{self.v2}/test?key={self._cs_api}').json()

    def ping_pong(self):
        """Раз в 3 минуты отправить, что я на сайте"""
        result = requests.get(f'{self.v2}/ping/?key={self._cs_api}').json()
        for key, value in result.items():
            if value or value == 'pong':
                pass
            else:
                raise print(f'{key} нет доступа: ответ {value}')
        return True

    def balance(self):
        """Баланс"""
        return requests.get(f'{self.v2}/get-money/?key={self._cs_api}').json()

    def remove_all_from_sale(self):
        """Снятие сразу всех предметов с продажи."""
        return requests.get(f'{self.v2}/remove-all-from-sale?key={self._cs_api}').json()

    def sell(self, item, price=10000000):
        """Выставить лот на продажу"""
        price = "{0:.0f}".format(price * 100)
        data = requests.get(f'{self.v2}/add-to-sale?key={self._cs_api}&id={item.id[0]}&price={price}&cur=RUB').json()
        if not data['success']:
            print('Не продали:', item.name, data)
            return False
        item.id_sell = data['item_id']
        return data

    def all_order_item(self, class_id: str, instance_id: str):
        """Все ордера на продажу"""
        return requests.get(f'{self.v1}/SellOffers/{class_id}_{instance_id}/?key={self._cs_api}').json()

    def search_item_by_name(self, hash_name: str):
        """Поиск предмета по hash имени"""
        return requests.get(f'{self.v2}/search-item-by-hash-name?key={self._cs_api}&hash_name={hash_name}').json()

    def search_item_by_name_5(self, data):
        """Поиск предмета по hash имени макс. 5"""
        a = {}
        data1 = ''
        for i in data:
            data1 += f'&list_hash_name[]=' + i.name
        a.update(requests.get(f'{self.v2}/search-list-items-by-hash-name-all?'
                              f'key={self._cs_api}&extended=1{data1}').json()['data'])
        for i in data:
            if i.name in a:
                i.sell_orders = [float(item['price']) / 100 for item in a[i.name]]
            else:
                i.sell_orders = [float(i.avg_result * 0.4 + i.avg_result)]
        return data

    def search_item_by_name_50(self, data: list) -> None:
        """Запрос 50 предметов за раз"""

        complete_50_items = '&list_hash_name[]='.join(set([i.hash_name for i in data]))
        response = requests.get(f'{self.v2}/search-list-items-by-hash-name-all?'
                                f'key={self._cs_api}&list_hash_name[]={complete_50_items}').json()['data']
        for i in data:
            if i.hash_name in response:
                i.sell_orders = [float(item['price']) / 100 for item in response[i.hash_name]]
            else:
                i.sell_orders = [float(i.avg_result * 0.4 + i.avg_result)]

    def trade_request_all(self):
        """Все сделки, которые нужно подтвердить, приходит LIST( {'appid', 'context_id', 'assetid'(при подпадении
         можно найти в инвентаре при нажатии правой кнопкой мыши), 'amount'}"""
        return requests.get(f'{self.v2}/trade-request-give-p2p-all?key={self._cs_api}').json()

    def set_price(self, item, price: float):
        """Изменить цену лота, ответ dict {'success': True} цена  - 0 снятие """
        data = requests.get(
            f'{self.v2}/set-price?key={self._cs_api}&item_id={item.id_sell}&price={price}&cur=RUB').json()
        return data

    def history(self, items):
        """История продаж предметов, макс. 100 post
        Пример:
        a = trader.history({"list": [dd]})"""
        return requests.post(f'{self.v1}/MassInfo/0/0/0/1?key={self._cs_api}', data=items).json()

    def item_info(self, class_id: str, instance_id: str):
        return requests.get(f'{self.v1}/ItemInfo/{class_id}_{instance_id}/ru/?key={self._cs_api}').json()

    def trade_request_give_p2p_all(self) -> list[Any] | int:
        response = requests.get(f'https://market.csgo.com/api/v2/trade-request-give-p2p-all?key={self._cs_api}').json()
        if response['success']:
            return [CreatOfferts(**i) for i in response['offers']]
        return 0
