from bd.models import Session_cs, Items
from confirmation import ConfirmationExecutor
from api_cs_market import RequestsCS
from models import ItemsConfirm
from variables import IDENTITY_SECRET, STEAM_ID, ANDROID
from auth_bots import *

session = creation_session_bots()['_kornelius_']

confirm = RequestsCS()

# a = confirm.trade_request_all()
# items_confirm = ItemsConfirm(**a)
#
#
# with Session_cs() as _session:
#     name_in_base = [b.assetid for i in items_confirm.offers for b in i.items]
#     data_bd = _session.query(Items)\
#         .filter(Items.id.in_(name_in_base))\
#         .all()

    # for i in items_confirm.offers:
    #     for i1 in i.items:
    #         i1.name = [appid[1] for appid in data_bd if appid[0] == i1.assetid][0]

data_bd = []
ConfirmationExecutor(
    identity_secret=IDENTITY_SECRET,
    my_steam_id=STEAM_ID,
    session=session,
    adnroid=ANDROID,
    items_confirm=data_bd).confirm_sell_listing()

print()
