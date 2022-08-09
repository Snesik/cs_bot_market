import time

from cs_bot.models_API import Inventory
from bd.models import Items, Price, Status, engine_bd_cs, engine_bd_full_base
from api_cs_market import RequestsCS
from cs_bot.models import SellInfo
from cs_bot.utils import chunks
from tqdm.contrib.concurrent import process_map
from sqlalchemy import update, select
from sqlalchemy.orm import Session
import requests
import concurrent.futures

trader = RequestsCS()

session = Session(bind=engine_bd_cs)
session_full_base = Session(bind=engine_bd_full_base)


def find_instance_id(asset_id):
    head = {'Referer': f"https://steamcommunity.com/profiles/76561198073787208/inventory"}
    all_intem = requests.get('https://steamcommunity.com/inventory/76561198073787208/730/2?l=russian&count=5000',
                             headers=head).json()
    return [item['instanceid'] for item in all_intem['assets']
            if item['assetid'] == asset_id and item['instanceid'] != 0][0]


def add_in_bd(inventory_items: list[Inventory]) -> None:
    lots_in_bd = [str(i[0]) for i in session.query(Items.id).all()]
    that_we_add_in_bd = [i for i in inventory_items if not i.id in lots_in_bd]
    for i in that_we_add_in_bd:
        if i.instanceid == '0':
            result = find_instance_id(i.id)
            if result is None:
                i.instanceid = 0
            else:
                i.instanceid = result

        intem = Items(
            id=i.id,
            name=i.market_hash_name,
            class_id=i.classid,
            instance_id=i.instanceid
        )
        price = Price(item_id=i.id)
        status = Status(item_id=i.id)
        session.add_all([intem, price, status])
        session.commit()


def chech_my_price(list_item_id) -> list:
    result_bd = session.query(Items.name, Items.id, Items.class_id, Price.sell, Items.instance_id) \
        .filter(Items.id == Price.item_id) \
        .filter(Items.id.in_(list_item_id)) \
        .all()
    all_inv_item = []
    for one_result in result_bd:
        if len(all_inv_item) == 0:
            all_inv_item.append(SellInfo(*one_result))
            continue
        for item in all_inv_item:
            if item.name == one_result[0]:
                if item.id == one_result[1]:
                    break
                else:
                    item.id = item.id + [str(one_result[1])]
                    break
        else:
            all_inv_item.append(SellInfo(*one_result))
    request_in_bd = tuple([item.href for item in all_inv_item])
    result = session_full_base.execute(f'SELECT ss, avg_result, low_avg FROM cs WHERE ss in {request_in_bd}')
    result = [row for row in result]
    for i in result:
        for item in all_inv_item:
            if item.href == i[0]:
                item.avg_result = i[1]
                item.low_avg = i[2]
                break
        else:
            print('Лота нету в наших лотах ', i[0])

    return all_inv_item


def traders(item):
    price = round((item.sell_orders[0] - 0.01), 2)
    data = trader.sell(item, price)
    # if price > item.low_avg:
    #     if price < item.min_price():
    #         if item.range_price() > 5:
    # #print(item.name)
    # data = trader.sell(item, price)
    # if not data:
    #     return False
    # if data:
    #     session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"sell": price},
    #                                                                         synchronize_session='fetch')
    #     session.query(Status).filter(Status.item_id.ilike(item.id[0])).update({"status": 'trad'},
    #                                                                           synchronize_session='fetch')
    #     session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"counter": 0},
    #                                                                         synchronize_session='fetch')
    #     session.commit()
    #     print(item.name)
    # return
    # else:
    # data = trader.sell(item, price)
    # if not data:
    #     return False
    # if data:
    #
    #     session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"sell": price},
    #                                                                         synchronize_session='fetch')
    #     session.query(Status).filter(Status.item_id.ilike(item.id[0])).update({"status": 'trad'},
    #                                                                           synchronize_session='fetch')
    #     session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"counter": 0},
    #                                                                         synchronize_session='fetch')
    #     session.commit()
    #
    #
    #     print(item.name)
    # return
    # session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"counter": Price.counter + 1},
    # synchronize_session='fetch')
    # session.commit()
    # print(f'НЕВЫСТАВИЛИ  {item.name} {item.href}')


trader.ping_pong()
trader.test()
trader.update_inv()
while True:
    add_in_bd(trader.my_inventory())
    result = chech_my_price([i.id for i in trader.my_inventory()])
    session = Session(bind=engine_bd_cs)
    session_full_base = Session(bind=engine_bd_full_base)

    traderss = trader.remove_all_from_sale()
    bb = trader.all_sell()
    #result = chech_my_price()
    for intem_50 in chunks(result, 50):
        trader.search_item_by_name_50(intem_50)

    # aa = AsynseRequests(result)
    from tqdm import tqdm

    start_time = time.time()


    def run(traders, result):
        try:
            # aa = session.query(Items)
            # for i in aa:
            #     print(i)
            # sss = all_data.filter(Items.id)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                sssss = executor.map(traders, result)
                return
        except:
            print()


    a = run(traders, result)
    session.connection()
    print("--- %s seconds ---" % (time.time() - start_time))
    time.sleep(240)


