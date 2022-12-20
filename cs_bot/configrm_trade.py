from bd import Session_cs
from bd.models import Items, Status
from confirmation import ConfirmationExecutor
from cs_bot.api_cs.api import RequestsCS
from models import ItemsConfirm
from variables import BOTS
from auth_bots import *
from pydantic.error_wrappers import ValidationError
import traceback
from datetime import datetime
import pprint

session_all_bots = creation_session_bots()

def start_confirm():
    while True:

        for BOT in BOTS:
            try:
                bot = BOTS[BOT]
                session = session_all_bots[BOT]
                confirm = RequestsCS(bot)
                # ss = confirm.create_trade_p2p()
                a = confirm.trade_request_all()
                try:
                    if a['success']:
                        items_confirm = ItemsConfirm(**a)
                    else:
                        time.sleep(5)
                        continue
                except ValidationError:
                    print('ОШИБКА ВАЛИДАТОРА', traceback.print_exc())
                    time.sleep(15)
                    items_confirm = ItemsConfirm(**confirm.trade_request_all())

                except Exception as error:
                    print('ОШИБКА ОБЩИЯ А НЕ ВАЛИДАЦИЯ', traceback.print_exc())
                    time.sleep(5)
                    continue

                with Session_cs() as _session:
                    name_in_base = [b.assetid for i in items_confirm.offers for b in i.items]
                    data_bd = _session.query(Items) \
                        .filter(Items.id.in_(name_in_base)) \
                        .all()

                bb = ConfirmationExecutor(
                    identity_secret=bot['config']['identity_secret'],
                    my_steam_id=bot['config']['steam_login_sec'],
                    session=session,
                    android=bot['config']['android'],
                    items_confirm=data_bd).send_trade_allow_request()

                for item in bb:
                    with Session_cs() as s:
                        s.query(Status) \
                            .filter(Status.item_id == item.id) \
                            .update({Status.status: 'sold'},
                                    synchronize_session='fetch'
                                    )
                        s.commit()
                if len(bb) > 0:
                    print(f'[{datetime.now()}] {bb}')
                time.sleep(25)
            except Exception:
                print("ОШИБКА ВО ВСЕМ КОДЕ")
                print(traceback.print_exc())
                time.sleep(10)
