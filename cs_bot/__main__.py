import datetime
import time
from models_API import Inventory
from bd.models import Items, Price, Status, Session_cs, Session_full_base
from api_cs_market import RequestsCS
from models import SellInfo
from utils import chunks
from variables import STEAM_LOGIN_ID
import requests
import concurrent.futures
from tqdm import tqdm

trader = RequestsCS()


def request_inventory_steam():
    head = {'Referer': f"https://steamcommunity.com/profiles/{STEAM_LOGIN_ID}/inventory"}
    all_intem = requests.get(f'https://steamcommunity.com/inventory/{STEAM_LOGIN_ID}/730/2?l=russian&count=5000',
                             headers=head).json()
    return all_intem


def find_instance_id_and_name(item_look, inventory_steam):
    instanceid = [item['instanceid'] for item in inventory_steam['assets']
                  if item['assetid'] == item_look.id][0]
    name = [item['name'] for item in inventory_steam['descriptions']
            if item['market_hash_name'] == item_look.market_hash_name][0]
    return instanceid, name


# 'descriptions'

def add_in_bd(inventory_items: list[Inventory]) -> None:
    all_cs_inventory = request_inventory_steam()
    with Session_cs() as session:
        lots_in_bd = [str(i[0]) for i in session.query(Items.id).all()]
        that_we_add_in_bd = [i for i in inventory_items if not i.id in lots_in_bd]
        print(f'Добавления лотов в базу.  TIME: {datetime.datetime.now()}')
        for i in tqdm(that_we_add_in_bd, total=len(that_we_add_in_bd)):
            instanceid, name = find_instance_id_and_name(i, all_cs_inventory)
            intem = Items(
                id=i.id,
                name=name,
                hash_name=i.market_hash_name,
                class_id=i.classid,
                instance_id=instanceid
            )
            price = Price(item_id=i.id)
            status = Status(item_id=i.id)
            session.add_all([intem, price, status])
            session.commit()


def chech_my_price(list_item_id) -> list:
    with Session_cs() as session:
        result_bd = session.query(Items.hash_name, Items.id, Items.class_id, Price.sell, Items.instance_id) \
            .filter(Items.id == Price.item_id) \
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
    # data = trader.sell(item, price)
    if price > item.low_avg:
        if price < item.min_price():
            if item.range_price() > 5:
                print(item.name)
    data = trader.sell(item, price)
    if data:
        with Session_cs() as session:
            session.query(Items) \
                .filter(
                Items.id == item.id[0],
                Items.id == Price.item_id,
                Items.id == Status.item_id) \
                .update(
                {Price.sell: price, Status.status: 'trad', },
                synchronize_session='fetch'
            )
            session.commit()
        # print(item.name)
        return
    else:
        data = trader.sell(item, price)
    if data:
        with Session_cs() as session:
            session.query(Items) \
                .filter(
                Items.id == item.id[0],
                Items.id == Price.item_id,
                Items.id == Status.item_id) \
                .update(
                {Price.sell: price, Status.status: 'trad', },
                synchronize_session='fetch'
            )
            session.commit()

        # print(item.name)
        return
    with Session_cs() as session:
        session.query(Price).filter(Price.item_id.ilike(item.id[0])).update({"counter": Price.counter + 1},
                                                                            synchronize_session='fetch')
        session.commit()
    print(f'НЕВЫСТАВИЛИ  {item.name} {item.href}')


trader.ping_pong()
trader.test()
trader.update_inv()
while True:
    add_in_bd(trader.my_inventory())
    result = chech_my_price([i.id for i in trader.my_inventory()])
    # session = Session(bind=engine_bd_cs)
    # session_full_base = Session(bind=engine_bd_full_base)

    traderss = trader.remove_all_from_sale()
    bb = trader.all_sell()
    # result = chech_my_price()
    for intem_50 in chunks(result, 50):
        trader.search_item_by_name_50(intem_50)

    # aa = AsynseRequests(result)

    start_time = time.time()


    def run(traders, result):
        try:
            # aa = session.query(Items)
            # for i in aa:
            #     print(i)
            # sss = all_data.filter(Items.id)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                print(f'Выставляем лоты на продажу,  TIME: {datetime.datetime.now()}')
                sssss = list(tqdm(executor.map(traders, result),
                                  unit=' Лот', colour='green',
                                  total=len(result)))
            # thread_map(traders, result, max_workers=5)
            return
        except:
            print()


    a = run(traders, result)
    # session.connection()
    print("--- %s seconds ---" % (time.time() - start_time))
    time.sleep(240)
