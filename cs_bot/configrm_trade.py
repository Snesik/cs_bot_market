from api_cs_market import RequestsCS
from models import ItemsConfirm, Item, Offer




confirm = RequestsCS()

a = confirm.trade_request_all()
print()
