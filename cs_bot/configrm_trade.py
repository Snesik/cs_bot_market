import requests
from confirmation import ConfirmationExecutor
from api_cs_market import RequestsCS
from models import ItemsConfirm
from variables import IDENTITY_SECRET, STEAM_ID, ANDROID
from auth_bots import *



session = creation_session_bots()['_kornelius_']

confirm = RequestsCS()

a = confirm.trade_request_all()
ss = ItemsConfirm(**a)

ConfirmationExecutor(
    identity_secret=IDENTITY_SECRET,
    my_steam_id=STEAM_ID,
    session=session,
    adnroid=ANDROID).confirm_sell_listing()





print()
