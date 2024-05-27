from AdServices.AdService import AdService
from AdServices.PlacementsId.ChartBoostPlacementsId import ChartBoostPlacementsKids, ChartBoostPlacementsAdults
from DataBase.MySql import MySql
from Config.config import CHARBOOST_CLIENT_ID, CHARBOOST_CLIENT_SECRET, DB_SENDER_HOST, DB_SENDER_USER, \
    DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import *
import requests
import json
from Enums.Enums import AdFormats, ChartBoostAdFormats
from Convertors.InputTo1CConvertor import InputTo1CConvertor


def get_placement_name(is_android, template):
    if is_android:
        answer = 'a_' + template
    else:
        answer = 'i_' + template
    return answer


def get_def_name(is_android, ad_format, bundle=None):
    if bundle:
        answer = f'a._.Default.{bundle}' if is_android else f'i._.Default.{bundle}'
    else:
        answer = '_.Default' if is_android else '_.Default'
    if ad_format == AdFormats.inter:
        answer = answer.replace('_', 'i')
    elif ad_format == AdFormats.banner:
        answer = answer.replace('_', 'b')
    else:
        answer = answer.replace('_', 'v')
    return answer


class CharBoost(AdService):

    def __init__(self,
                 bundle: str,
                 store_app_id: str,
                 ad_formats: [],
                 orientations: [str, str],
                 is_android: bool,
                 kids: bool):
        super().__init__()
        self.cl_id = CHARBOOST_CLIENT_ID
        self.cl_sec = CHARBOOST_CLIENT_SECRET
        self.base_url = 'https://api.chartboost.com'
        self.bundle = bundle
        self.ad_formats = ad_formats
        self.store_app_id = store_app_id
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.is_android = is_android
        self.orientations = orientations
        self.kids = kids
        self.placements = self.get_placements()
        self.token = self.get_token()
        self.message = 'Успішно. '

    def get_placements(self):
        my_class = ChartBoostPlacementsKids() if self.kids else ChartBoostPlacementsAdults()
        template = {}
        if AdFormats.banner in self.ad_formats:
            template.update(**my_class.get_banner())
        if AdFormats.inter in self.ad_formats:
            template.update(**my_class.get_interstitial())
        if AdFormats.reward in self.ad_formats:
            template.update(**my_class.get_rewarded())
        if not template:
            raise ChartBoostPlacementsException
        return template

    @staticmethod
    def get_price(placement):
        return float(placement[2:].replace('_', '.'))

    @staticmethod
    def get_mark(name, is_bid=True) -> str:
        if 'def' in name.lower() or 'bid' in name.lower():
            if is_bid:
                return 'Bid'
            else:
                return 'Def'
        else:
            return name[2:]

    @staticmethod
    def get_ad_type(placement_id) -> str:
        match placement_id[2]:
            case 'i':
                return ChartBoostAdFormats.inter.value
            case 'v':
                return ChartBoostAdFormats.reward.value
            case _:
                return ChartBoostAdFormats.banner.value

    def get_token(self):
        import base64
        secret = f'{self.cl_id}:{self.cl_sec}'
        secret = base64.b64encode(secret.encode()).decode()

        req = requests.post(url=self.base_url + '/v4/token',
                            headers={'Host': 'api.chartboost.com',
                                     'Authorization': f'Basic {secret}',
                                     'Content-Type': 'application/x-www-form-urlencoded'},
                            data={'grant_type': 'client_credentials'})

        if req.status_code != 200 and req.status_code != 201:
            raise ConnectionError

        return req.json().get('access_token')

    def create_app(self):
        url = self.base_url + '/v4/apps'
        body = {
            'nickname': self.bundle,
            'orientations': self.orientations,
            'default_orientation': self.orientations[0],
            'is_live': True,
            'store_app_id': self.bundle,
            'store_app_url': self.link,
            'store_bundle_id': self.store_app_id,  # looks weird, but CAS named app_id as bundle :_(
            'is_test_mode_on': False,
            'is_directed_at_kids_under_13': "YES" if self.kids else "NO",
            'platform': 'android' if self.is_android else 'ios'
        }

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        req = requests.post(
            url=url,
            headers=headers,
            json=body
        )

        if req.status_code != 200 and req.status_code != 201:
            raise CannotCreateApp

        return req.json().get('id'), req.json().get('signature')

    def add_placements(self, app_id: str, placement_name: str, ad_type: str, price: float):
        url = self.base_url + f'/v4/apps/{app_id}/ad-locations'

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        data = {
            'name': placement_name,
            'ad_type': ad_type,
            'type': 'fixed_cpm',
            'country_targeting': [
                {
                    "country": "default",
                    "price": price
                }
            ]
        }

        req = requests.post(
            url=url,
            headers=headers,
            json=data
        )

        if req.status_code != 200 and req.status_code != 201:
            raise ProblemsWithPlacementCreation

        return {
            'name': placement_name,
            'ad_type': ad_type
        }

    def auto_writing(self):
        app_id, signature = self.create_app()
        info = []

        for placement in self.placements:
            info.append(
                self.add_placements(
                    app_id=app_id,
                    placement_name=get_placement_name(self.is_android, placement),
                    ad_type=CharBoost.get_ad_type('x.' + placement),
                    price=self.get_price(placement)
                ))

        info_to_send = []

        for unit in info:
            info_to_send.append(
                json.dumps({
                    'name': unit.get('name').replace('_', '.') + '.' + self.bundle + ' Chartboost',
                    'appId': app_id,
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit.get('name')),
                    'platform': self.get_platform(self.is_android),
                    'account': 'Chartboost',
                    'id': unit.get('name'),
                    'signature': signature,
                    'mark': CharBoost.get_mark(unit.get('name')[2:].replace('_', '.'), is_bid=False),
                })
            )

        for ad_format in self.ad_formats:
            info_to_send.append(
                json.dumps({
                    'name': get_def_name(is_android=self.is_android, ad_format=ad_format, bundle=self.bundle),
                    'appId': app_id,
                    'app': self.bundle,
                    'bannerType': InputTo1CConvertor.ad_format(ad_format).value,
                    'platform': self.get_platform(self.is_android),
                    'account': 'Chartboost',
                    'id': 'Default',
                    'signature': signature,
                    'mark': 'Def',
                    'status': 0,  # В 1С стоятиме НЕ вигружать
                })
            )

        data_base_to_send = MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT)

        for info in info_to_send:
            data_base_to_send.send_to_1c(
                ad_service='Chartboost',
                json=info,
                username=self._user_name
            )

        return True, self.message


# a = CharBoost(bundle='com.xishanju.codess.intl', store_app_id='com.xishanju.codess.intl',
#               orientations=['landscape', 'portrait'], is_android=True, kids=True,
#               ad_formats=[AdFormats.inter, AdFormats.reward, AdFormats.banner]).auto_writing()
