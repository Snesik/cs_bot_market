import enum
import time
import re
import requests
from typing import List
from bs4 import BeautifulSoup
from steampy import guard
from models import ItemSteamConfirm


class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self,
                 identity_secret: str,
                 my_steam_id: str,
                 session: requests.Session,
                 android: str,
                 items_confirm: list
                 ) -> None:

        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session
        self._android = android
        self._items_confirm = items_confirm

    def send_trade_allow_request(self) -> list:
        we_confirm = []
        result = self._get_confirmations()
        for r in result:
            for item in self._items_confirm:
                if r.name == item.name and r.data_accept == 'Отправить':
                    we_confirm.append(r)
                    break

        for i in we_confirm:
            for i2 in self._items_confirm:
                if i.name == i2.name:
                    i.id = i2.id
                    break

        self._multi_confirm_trans(we_confirm)
        return we_confirm

    def _get_confirmations(self) -> list:
        result = []
        confirmations_page = self._fetch_confirmations_page()
        soup = BeautifulSoup(confirmations_page, 'html.parser')
        if len(soup.select('.mobileconf_list_entry')) == 0:
            soup = BeautifulSoup(confirmations_page, 'html.parser')
        for item in soup.select('.mobileconf_list_entry'):
            item.attrs['name'] = re.findall('Обменять (.+?) на ', item.text)[0]
            result.append(ItemSteamConfirm(
                data_confid=item.attrs['data-confid'],
                data_key=item.attrs['data-key'],
                name=item.attrs['name'],
                data_accept=item.attrs['data-accept'],
                id='0'
            ))
        return result

    def _fetch_confirmations_page(self) -> str:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        headers = {'X-Requested-With': 'com.valvesoftware.android.steam.community'}
        response = self._session.get('https://steamcommunity.com/mobileconf/conf',
                                     params=params, headers=headers, timeout=60).text
        return response

    def _fetch_confirmation_details_page(self, confirmation) -> str:
        tag = 'details' + confirmation.id
        params = self._create_confirmation_params(tag)
        response = self._session.get(self.CONF_URL + '/details/' + confirmation.id, params=params)
        if response.json()['success']:
            return response.json()['html']
        else:
            response = self._fetch_confirmation_details_page(confirmation)
            return response

    def _multi_confirm_trans(self, we_confirm) -> None:
        tag = Tag.ALLOW
        params = self._create_confirmation_params(tag.value)
        params['op'] = tag.value,
        params_list = list(params.items())
        for conf in we_confirm:
            params_list.append(('cid[]', conf.data_confid))
            params_list.append(('ck[]', conf.data_key))
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        return self._session.post(self.CONF_URL + '/multiajaxop',
                                  data=params_list, headers=headers, timeout=60).json()

    def _create_confirmation_params(self, tag_string) -> dict:
        timestamp = int(time.time())
        confirmation_key = guard.generate_confirmation_key(self._identity_secret, tag_string, timestamp)
        android_id = self._android
        return {'p': android_id,
                'a': self._my_steam_id,
                'k': confirmation_key,
                't': timestamp,
                'm': 'android',
                'tag': tag_string,
                'op': tag_string
                }
