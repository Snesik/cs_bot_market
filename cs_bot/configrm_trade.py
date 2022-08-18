from bd import Session_cs
from bd.models import Items, Status
from confirmation import ConfirmationExecutor
from cs_bot.api_cs.api import RequestsCS
from models import ItemsConfirm
from variables import IDENTITY_SECRET, STEAM_ID, ANDROID
from auth_bots import *
import traceback
import pprint

session = creation_session_bots()['_kornelius_']
confirm = RequestsCS()
while True:
    try:
        a = confirm.trade_request_all()
        try:
            if a['success']:
                items_confirm = ItemsConfirm(**a)
            else:
                time.sleep(60)
                continue
        except Exception as error:
            print(traceback.print_exc())
            time.sleep(60)
            continue

        with Session_cs() as _session:
            name_in_base = [b.assetid for i in items_confirm.offers for b in i.items]
            data_bd = _session.query(Items) \
                .filter(Items.id.in_(name_in_base)) \
                .all()

        bb = ConfirmationExecutor(
            identity_secret=IDENTITY_SECRET,
            my_steam_id=STEAM_ID,
            session=session,
            android=ANDROID,
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
            pprint.pprint(bb, width=1)
        time.sleep(60)

    except Exception:
        time.sleep(60)