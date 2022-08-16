import enum
import json
import time
import re
import traceback
from typing import List
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from steampy import guard
from steampy.exceptions import ConfirmationExpected
from steampy.login import InvalidCredentials
from html.parser import HTMLParser
from utils import hash_in_name
from models import ItemSteamConfirm

class Confirmation:
    def __init__(self, _id, data_confid, data_key, price):
        self.id = _id.split('conf')[1]
        self.data_confid = data_confid
        self.data_key = data_key
        self.data_price = price


class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, my_steam_id: str, session: requests.Session, adnroid) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session
        self._adnroid = adnroid
        #self._assetid = assetid

    def send_trade_allow_request(self, trade_offer_id: str) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_trade_offer_confirmation(confirmations, trade_offer_id)
        return self._send_confirmation(confirmation)

    def confirm_sell_listing(self) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_sell_listing_confirmation(confirmations)
        # self._send_confirmation(confirmation)
        return self._assetid

    def _send_confirmation(self, data):
        tag = Tag.ALLOW

        try:

            params = self._create_confirmation_params(tag.value)
            params['cid'] = []
            params['ck'] = []
            for i in data:
                params['cid'].append(i.data_confid)
                params['ck'].append(i.data_key)
                # params['cid'] = confirmation.data_confid
                # params['ck'] = confirmation.data_key
            headers = {'X-Requested-With': 'XMLHttpRequest'}
            return self._session.get(self.CONF_URL + '/multiajaxop', params=params, headers=headers).json()
        except:
            # print(f'Ошибка в потверждение лота')
            return 'Ошибка'

    def _get_confirmations(self) -> List[Confirmation]:
        confirmations = []
        print('Потверждаем лоты sell')
        confirmations_page = self._fetch_confirmations_page()
        soup = BeautifulSoup(confirmations_page, 'html.parser')
        for item in soup.select('.mobileconf_list_entry'):
            item.attrs['name'] = re.findall('Обменять (.+?) на ', item.text)[0]
            a = ItemSteamConfirm(data_confid=item.attrs['data-confid'],
                                 data_key=item.attrs['data-key'],
                                 name=item.attrs['name']
                                 )
            print(a)

        for confirmation_div in soup.select('#mobileconf_list .mobileconf_list_entry'):
            _id = confirmation_div['id']
            data_confid = confirmation_div['data-confid']
            data_key = confirmation_div['data-key']
            price = re.findall(r'(.+?) pуб', confirmation_div.text)[0]
            confirmations.append(Confirmation(_id, data_confid, data_key, price))
        return confirmations

    def _fetch_confirmations_page(self) -> str:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        headers = {'X-Requested-With': 'com.valvesoftware.android.steam.community'}
        response = self._session.get('https://steamcommunity.com/mobileconf/conf', params=params).text
        # if 'Steam Guard Mobile Authenticator is providing incorrect Steam Guard codes.' in response.text:
        #     raise InvalidCredentials('Invalid Steam Guard file')
        return response

    def _fetch_confirmation_details_page(self, confirmation: Confirmation) -> str:
        tag = 'details' + confirmation.id
        params = self._create_confirmation_params(tag)
        response = self._session.get(self.CONF_URL + '/details/' + confirmation.id, params=params)

        # для индификации используется имя предмета, НЕ HASH NAME а именно имя предмета, берется из инвентаря
        # Вытащить только предметы котором требуется потверждение
        # response = self._session.get('https://steamcommunity.com/mobileconf/conf', params=params).text - Увидеть все лоты для потверждения
        #soup = BeautifulSoup(response, 'html.parser')
        #soup.select('.mobileconf_list_entry')
        #a = soup.select('.mobileconf_list_entry')[0].text
        #re.findall('Обменять (.+?) на ', a)  name
        # soup.select('.mobileconf_list_entry')[0].attrs data


        if response.json()['success']:
            return response.json()['html']
        else:
            response = self._fetch_confirmation_details_page(confirmation)
            return response

    def _multi_confimm_trans(self, confirmations):
        tag = Tag.ALLOW
        params = self._create_confirmation_params(tag.value)
        params['op'] = tag.value,
        params_list = list(params.items())
        for conf in confirmations:
            params_list.append(('cid[]', conf.data_confid))
            params_list.append(('ck[]', conf.data_key))
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        return self._session.post(self.CONF_URL + '/multiajaxop',
                                  data=params_list, headers=headers, timeout=60).json()

    def _create_confirmation_params(self, tag_string: str) -> dict:
        timestamp = int(time.time())
        confirmation_key = guard.generate_confirmation_key(self._identity_secret, tag_string, timestamp)
        android_id = self._adnroid
        #android_id = guard.generate_device_id(self._my_steam_id)
        return {'p': android_id,
                'a': self._my_steam_id,
                'k': confirmation_key,
                't': timestamp,
                'm': 'android',
                'tag': tag_string,
                'op': tag_string
                }

    def _select_trade_offer_confirmation(self, confirmations: List[Confirmation], trade_offer_id: str) -> Confirmation:
        for confirmation in tqdm(confirmations, ascii='_$',
                                 colour='green', desc='Ищем перебитые, завышеные лоты', ncols=200):
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_trade_offer_id(confirmation_details_page)
            if confirmation_id == trade_offer_id:
                return confirmation
        raise ConfirmationExpected

    def _select_sell_listing_confirmation(self, confirmations: List[Confirmation]):
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(confirmation)
            confirmation_id = self._get_confirmation_sell_listing_id(confirmation_details_page)
            for asset_one in self._assetid:
                if asset_one.asset_id == confirmation_id:
                    asset_one.sell = (re.sub(',', '.', confirmation.data_price)).strip()
        print('Лоты потвердили: ', self._multi_confimm_trans(confirmations))

        # except Exception as e:
        # print(e)
        # if confirmation_id == self._assetid:

        # return

        # raise ConfirmationExpected

    @staticmethod
    def _get_confirmation_sell_listing_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        scr_raw = soup.select("script")[2].string.strip()
        scr_raw = scr_raw[scr_raw.index("'confiteminfo', ") + 16:]
        scr_raw = scr_raw[:scr_raw.index(", UserYou")].replace("\n", "")
        return json.loads(scr_raw)["id"]

    @staticmethod
    def _get_confirmation_trade_offer_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, 'html.parser')
        full_offer_id = soup.select('.tradeoffer')[0]['id']
        return full_offer_id.split('_')[1]

