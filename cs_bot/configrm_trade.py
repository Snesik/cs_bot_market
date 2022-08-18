from bd import Session_cs
from bd.models import Items
from confirmation import ConfirmationExecutor
from api_cs.api_cs_market import RequestsCS
from models import ItemsConfirm
from variables import IDENTITY_SECRET, STEAM_ID, ANDROID
from auth_bots import *

session = creation_session_bots()['_kornelius_']

confirm = RequestsCS()

a = confirm.trade_request_all()
if a['success']:
    items_confirm = ItemsConfirm(**a)
else:
    raise print('error')

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

print()
