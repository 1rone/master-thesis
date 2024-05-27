import hashlib
import json
import time
import requests
from AdServices.AdService import AdService
from AdServices.Mediators.IronSourceMediation import IronSource
from AdServices.Mediators.MaxMediation import MaxMediation
from Convertors.PangleToMaxConvertor import PangleToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Convertors.PangleToIronSourceConvertor import PangleToIronSourceConvertor
from Enums.Enums import AdFormats, Mediators, MaxAdNetworks, IronSourceAdNetworks as IS
from DataBase.MySql import MySql
from Config.config import PANGLE_SECURITY_KEY, PANGlE_USER_ID, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import *


#  blocking rules ids
#  Children — 523256
#  Teens up to 17+ — 523208
#  Mature: азартных игр, алкоголя, знакомств, политики — 523207


class Pangle(AdService):

    def __init__(self, bundle, app_category, is_android, coppa, block_category_id, ad_format, orientation, mediation):
        super().__init__()

        def get_sign(sec_key, timestamp, nonce):
            keys = [sec_key, str(timestamp), str(nonce)]
            keys.sort()
            key_str = ''.join(keys)
            signature = hashlib.sha1(key_str.encode()).hexdigest()
            return signature

        self.sec_key = PANGLE_SECURITY_KEY
        self.timestamp = int(time.time())
        self.user_id = PANGlE_USER_ID
        self.app_category = app_category
        self.bundle = bundle
        self.is_android = is_android
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.coppa = coppa
        self.mediation = mediation
        self.message = 'Успішно. '
        self.block_category_id = block_category_id
        self.sign = get_sign(sec_key=self.sec_key,
                             timestamp=self.timestamp,
                             nonce=self.user_id)
        self.ad_format = ad_format
        self.orientation = orientation

    def create_app(self):
        url = 'https://open-api.pangleglobal.com/union/media/open_api/site/create'

        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }

        body = {
            'user_id': self.user_id,
            'role_id': self.user_id,
            'sign': self.sign,
            'timestamp': self.timestamp,
            'nonce': self.user_id,
            'version': '1.0',
            'app_name': self.bundle[:40],
            'status': 2,
            'app_category_code': self.app_category,
            'download_url': self.link,
            'coppa_value': self.coppa,
        }
        if self.block_category_id:
            body.update({'mask_rule_ids': self.block_category_id})

        req = requests.post(url=url,
                            headers=headers,
                            json=body)

        if req.status_code == 200:
            if json.loads(req.text).get('code') == 0:
                return json.loads(req.text).get('data').get('app_id')
            elif '21017' in json.loads(req.text).get('message'):
                raise AlreadyCreatedApp
            else:
                print(req.text)
                raise WrongInternalCode

        else:
            raise CannotCreateApp

    def update_app_category(self, app_id):
        url = 'https://open-api.pangleglobal.com/union/media/open_api/site/update'

        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }

        body = {
            'user_id': self.user_id,
            'role_id': self.user_id,
            'sign': self.sign,
            'timestamp': self.timestamp,
            'nonce': self.user_id,
            'version': '1.0',
            'app_id': app_id,
            'app_category_code': 120403,
        }

        requests.post(url=url,
                      headers=headers,
                      data=json.dumps(body))

        print(2)

    def create_placement(self, app_id, ad_format):

        def get_ad_slot_type():
            match ad_format:
                case AdFormats.banner:
                    return 2
                case AdFormats.inter:
                    return 6
                case AdFormats.reward:
                    return 5
                case _:
                    raise WrongPlacementTypeException

        def get_ad_slot_name():
            if self.is_android:
                slot_name = 'a.'
            else:
                slot_name = 'i.'
            match ad_format:
                case AdFormats.banner:
                    slot_name += 'b.bid'
                case AdFormats.inter:
                    slot_name += 'i.bid'
                case AdFormats.reward:
                    slot_name += 'v.bid'
                case _:
                    raise WrongPlacementTypeException
            return slot_name

        url = 'https://open-api.pangleglobal.com/union/media/open_api/code/create'

        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }

        name = get_ad_slot_name()

        data = {
            'user_id': self.user_id,
            'role_id': self.user_id,
            'sign': self.sign,
            'timestamp': self.timestamp,
            'nonce': self.user_id,
            'version': '1.0',
            'app_id': app_id,
            'ad_slot_type': get_ad_slot_type(),
            'ad_slot_name': name,
            'bidding_type': 2 if self.mediation == Mediators.CAS.value else 1,
            'render_type': 1,
        }

        match ad_format:
            case AdFormats.banner:
                data.update(
                    {'slide_banner': 1,
                     'width': 640,
                     'height': 100}
                )
            case AdFormats.reward:
                data.update(
                    {'orientation': 1 if self.orientation == 'vertical' else 2,
                     'reward_name': name,
                     'reward_count': 1,
                     'reward_is_callback': 0}
                )
            case AdFormats.inter:
                data.update({
                    'orientation': 1 if self.orientation == 'vertical' else 2,
                    'accept_material_type': 3
                })
            case _:
                raise WrongPlacementTypeException

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        if req.status_code == 200:
            if json.loads(req.text).get('code') == 0:
                return {name: json.loads(req.text).get('data').get('ad_slot_id')}
            else:
                print(req.text)
                raise WrongInternalCode

        else:
            raise ProblemsWithPlacementCreation

    def auto_writing(self):
        app_id = self.create_app()

        info = {}

        for ad_format in self.ad_format:
            info.update(self.create_placement(app_id=app_id,
                                              ad_format=ad_format))

        info_to_send = []

        is_info = {}

        for unit in info:
            info_to_send.append(
                json.dumps({
                    'name': unit + f'.{self.bundle}' + ' Pangle',
                    'appId': app_id,
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit),
                    'platform': self.get_platform(self.is_android),
                    'account': 'Pangle',
                    'rtb': info[unit],
                    'accountID': self.user_id,
                    'mark': self.get_mark(unit, is_bid=True),
                    'mediation': MediationTo1cConvertor.convert(self.mediation)
                })
            )

            if unit[2] == 'i':
                is_info['inter'] = str(info[unit])

            if unit[2] == 'b':
                is_info['banner'] = str(info[unit])

            if unit[2] == 'v':
                is_info['reward'] = str(info[unit])

            if self.mediation == Mediators.MAX.value:

                try:
                    # ЦЕ ПРАЦЮЄ ТІЛЬКИ ПОКИ В НАС mark = 'Def'!!!!!!
                    message = MaxMediation(
                        ad_format=PangleToMaxConvertor.convert_ad_format(unit),
                        platform=PangleToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=PangleToMaxConvertor.convert_coppa(coppa=self.coppa),
                        ad_network=MaxAdNetworks.Pangle,
                        unit_id=info[unit],
                        app_key=None,
                        app_id=app_id
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type(unit)}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type(unit)}. '

        if self.mediation == Mediators.IS.value:
            try:
                message = IronSource(
                    ad_format=PangleToIronSourceConvertor.convert_ad_formats(placements=self.ad_format),
                    bundle=self.bundle,
                    kids=PangleToIronSourceConvertor.convert_coppa(self.coppa),
                    is_android=self.is_android,
                    taxonomy=None,
                    provider_name=IS.Pangle.value,
                    app_config1=app_id,
                    app_config2=None,
                    instances=is_info
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти. Для активації біддера, в Панглі включи Server-side bidding'
            except Exception:
                self.message += f'Не зміг додати в IronSource. '

        data_base_to_send = MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT)

        for info in info_to_send:
            data_base_to_send.send_to_1c(
                ad_service='Pangle',
                json=info,
                username=self._user_name
            )

        return True, self.message


# print(Pangle(app_category=120212,
#              bundle='com.movies.sfera',
#              block_category_id=[523207],
#              coppa=0,
#              is_android=True,
#              ad_format=[AdFormats.banner, AdFormats.reward, AdFormats.inter],
#              orientation='horizontal',
#              mediation=Mediators.IS.value).auto_writing())
