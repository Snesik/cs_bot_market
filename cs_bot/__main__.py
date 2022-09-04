import datetime
import time
import requests
import concurrent.futures
from tqdm import tqdm
from bd import Session_cs, Session_full_base
from cs_bot.api_cs.models import Inventory
from cs_bot.api_cs.api import RequestsCS
from cs_bot.bd.models import Items, Price, Status
from cs_bot.models import SellInfo
from cs_bot.utils import chunks
from variables import BOTS




def request_inventory_steam(steam_login_id):
    head = {'Referer': f"https://steamcommunity.com/profiles/{steam_login_id}/inventory"}
    all_item = requests.get(f'https://steamcommunity.com/inventory/{steam_login_id}/730/2?l=russian&count=5000',
                            headers=head).json()
    return all_item


def find_instance_id_and_name(item_look, inventory_steam):
    instance_id = [item['instanceid'] for item in inventory_steam['assets']
                   if item['assetid'] == item_look.id][0]
    name = [item['name'] for item in inventory_steam['descriptions']
            if item['market_hash_name'] == item_look.market_hash_name][0]
    return instance_id, name


def add_in_bd(inventory_items: list[Inventory], bot) -> None:
    all_cs_inventory = request_inventory_steam(bot['steam_id'])
    with Session_cs() as session:
        lots_in_bd = [str(i[0]) for i in session.query(Items.id).all()]
        that_we_add_in_bd = [i for i in inventory_items if not i.id in lots_in_bd]
        print(f'Добавления лотов в базу.  TIME: {datetime.datetime.now()}')
        for i in tqdm(that_we_add_in_bd, total=len(that_we_add_in_bd)):
            instance_id, name = find_instance_id_and_name(i, all_cs_inventory)
            item = Items(
                id=i.id,
                name=name,
                hash_name=i.market_hash_name,
                class_id=i.classid,
                instance_id=instance_id
            )
            price = Price(item_id=i.id)
            status = Status(item_id=i.id)
            session.add_all([item, price, status])
            session.commit()


def check_my_price(list_item_id) -> list:
    with Session_cs() as session:
        result_bd = session.query(Items.hash_name, Items.id, Items.class_id, Price.sell, Items.instance_id) \
            .filter(Items.id == Price.item_id) \
            .filter(Items.id == Status.item_id) \
            .filter(Items.id.in_(list_item_id)) \
            .all()

    all_inv_item = []
    for one_result in result_bd:
        if len(all_inv_item) == 0:
            all_inv_item.append(SellInfo(*one_result))
            continue
        for item in all_inv_item:
            if item.hash_name == one_result[0]:
                if item.id == one_result[1]:
                    break
                else:
                    item.id = item.id + [str(one_result[1])]
                    break
        else:
            all_inv_item.append(SellInfo(*one_result))
    request_in_bd = tuple([item.href for item in all_inv_item])
    with Session_full_base() as session_full_base:
        result_bd = session_full_base.execute(f'SELECT ss, avg_result, low_avg FROM cs WHERE ss in {request_in_bd}')
    result = [row for row in result_bd]
    for i in result:
        for item in all_inv_item:
            if item.href == i[0]:
                item.avg_result = i[1]
                item.low_avg = i[2]
                break
        else:
            print('Лота нету в наших лотах ', i[0])

    return all_inv_item


def sell_and_write_in_base(item, price):
    data = trader.sell(item, price)
    if data:
        with Session_cs() as session:
            session.query(Items) \
                .filter(
                Items.id == item.id[0],
                Items.id == Price.item_id,
                Items.id == Status.item_id
            ) \
                .update(
                {
                    Price.sell: price, Price.min_price: round(item.min_price(), 2), Price.counter: 0,
                    Status.status: 'trad'
                },
                synchronize_session='fetch'
            )
            session.commit()


def traders(item) -> None:
    price = round((item.sell_orders[0] - 0.01), 2)
    if item.range_price() > 8:
        sell_and_write_in_base(item, price)
        return
    elif price > item.min_price():
        sell_and_write_in_base(item, price)
        return
    with Session_cs() as session:
        session.query(Price) \
            .filter(Price.item_id == item.id[0]) \
            .update(
            {
                Price.counter: Price.counter + 1, Price.sell: price, Price.min_price: item.min_price()
            },
            synchronize_session='fetch')
        session.commit()


#trader.ping_pong()
# trader.test()
# trader.update_inv()
while True:
    for BOT in BOTS:
        try:
            bot = BOTS[BOT]
            trader = RequestsCS(bot)
            trader.update_inv()
            response_remove = trader.remove_all_from_sale()
            trader.update_inv()
            add_in_bd(trader.my_inventory(), bot)
            result_my_price = check_my_price([i.id for i in trader.my_inventory()])

            for item_50 in chunks(result_my_price, 50):
                trader.search_item_by_name_50(item_50)

            start_time = time.time()


            def run(func, result):
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        print(f'Выставляем лоты на продажу,  TIME: {datetime.datetime.now()}')
                        list(tqdm(executor.map(func, result),
                                  unit=' Лот', colour='green',
                                  total=len(result)))
                    return
                except Exception as error:
                    print(error)


            run(traders, result_my_price)
            print(BOT, trader.balance()['money'])
            time.sleep(120)
        except Exception:
            time.sleep(120)
