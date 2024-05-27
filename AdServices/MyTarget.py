import json
import requests
from AdServices.AdService import AdService
from AdServices.Mediators.MaxMediation import MaxMediation
from Config.config import DB_SENDER_HOST, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_USER, DB_SENDER_PORT
from Convertors.MyTargetToMaxConvertor import MyTargetToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Exceptions.Exceptions import *
from DataBase.MySql import MySql
import traceback
from Enums.Enums import AdFormats, Mediators, MaxAdNetworks


def get_plc_id(is_android, ad_format):
    # ids = {
    #     'ios': 6122,
    #     'android': 6123,
    #     'banner_android': 6125,
    #     'banner_ios': 6124,
    #     'interstitial_android': 6443,
    #     'interstitial_ios': 6440,
    #     'rewarded_android': 20297,
    #     'rewarded_ios': 20298
    # }

    if is_android:
        match ad_format:
            case AdFormats.banner:
                return 6125
            case AdFormats.inter:
                return 6443
            case AdFormats.reward:
                return 20297
            case _:
                raise WrongPlacementTypeException
    else:
        match ad_format:
            case AdFormats.banner:
                return 6124
            case AdFormats.inter:
                return 6440
            case AdFormats.reward:
                return 20298
            case _:
                raise WrongPlacementTypeException


class MyTarget(AdService):

    def __init__(self, bundle, is_android, ad_format, categories, mediation, kids):
        super().__init__()
        self.bundle = bundle
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.is_android = is_android
        self.ad_format = ad_format
        self.mediation = mediation
        self.kids = kids
        self.message = 'Успішно. '
        cookies = self.get_header(MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT).get_headers(
            ad_service='MyTarget',
            header_name='Cookie'))
        token = self.get_header(MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT).get_headers(
            ad_service='MyTarget',
            header_name='X-CSRFToken'))
        self.headers = {**cookies, **token}
        self.categories = categories

    def create_app(self):
        url = 'https://target.my.com/api/v2/group_pads.json'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en',
            'Host': 'target.my.com',
            'Origin': 'https://target.my.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Referer': 'https://target.my.com/create_group_pads',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        }

        headers.update(self.headers)

        data = {
            "url": self.link,
            "platform_id": 6123 if self.is_android else 6122,
            "description": self.bundle,
            "filters": {
                "deny_mobile_android_category": [],
                "deny_mobile_category": [],
                "deny_topics": self.categories,
                "deny_pad_url": [],
                "deny_mobile_apps": []
            },
        }

        pads = {"pads": []}

        for ad_format in self.ad_format:
            plc_name = ('a.' if self.is_android else 'i.') + (
                'b.' if ad_format == AdFormats.banner else 'v.' if ad_format == AdFormats.reward else 'i.') + 'bid'
            plc_id = get_plc_id(is_android=self.is_android,
                                ad_format=ad_format)
            pads["pads"].append(

                {
                    "description": plc_name,
                    "format_id": plc_id,
                    "filters": {},
                    "shows_period": "day",
                    "shows_limit": None,
                    "shows_interval": None,

                    "integration_type": "inapp_bidding",
                    "partner_a_block_cpm_limit": 0,
                    "partner_a_cpm_limit_geo": {}
                }

            )

        data.update(pads)

        req = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )

        match req.status_code:
            case 201:
                return json.loads(req.text).get('id')
            case 401:
                raise WrongToken
            case 400:
                if req.json().get('error').get('fields').get('url').get('code') == 'url_app_invalid':
                    raise CannotFindApp
                else:
                    print('status code=', req.status_code)
                    print('text=', req.text)
                    print(traceback.format_exc())
                    raise Exception
            case _:
                print('status code=', req.status_code)
                print('text=', req.text)
                print(traceback.format_exc())
                raise Exception

    def get_all_placements(self, app_id):
        url = f'https://target.my.com/api/v2/group_pads/{app_id}/pads.json'

        headers = {
            'Accept': '*/*',
            'Referer': f'https://target.my.com/partner/groups/{app_id}/pads',
            'Host': 'target.my.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Accept-Language': 'en',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        headers.update({'Cookie': self.headers.get('Cookie')})

        req = requests.get(url=url,
                           headers=headers)

        match req.status_code:
            case 200:
                placements = json.loads(req.text).get('items')
            case 401 | 403:
                raise WrongToken
            case _:
                print('status code=', req.status_code)
                print('text=', req.text)
                print(traceback.format_exc())
                raise Exception

        answer = {}

        for placement in placements:
            answer[placement.get('description')] = {'placement_id': placement.get('id'),
                                                    'slot_id': placement.get('slot_id')}

        return answer

    def activate_app_and_all_placements(self, placements_ids, app_id):
        url = 'https://target.my.com/api/v2/pads/mass_action.json'

        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en',
            'Host': 'target.my.com',
            'Origin': 'https://target.my.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Referer': f'https://target.my.com/partner/groups/{app_id}/pads',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        headers.update(self.headers)

        data = []

        for placement_id in placements_ids:
            data.append({
                "id": placement_id,
                "status": "active"
            })

        data.append({
            "id": app_id,
            "status": "active"
        })

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        match req.status_code:
            case 204:
                return True
            case 401:
                raise WrongToken
            case _:
                print('status code=', req.status_code)
                print('text=', req.text)
                print(traceback.format_exc())
                raise Exception

    def auto_writing(self):

        app_id = self.create_app()

        placements_ids = self.get_all_placements(app_id=app_id)

        self.activate_app_and_all_placements(
            placements_ids=[placements_ids[i].get('placement_id') for i in placements_ids],
            app_id=app_id)

        info_to_send = []

        is_info = {'slotId': {},
                   'PlacementID': {}}

        for unit in placements_ids:
            info_to_send.append(
                json.dumps({
                    'name': unit + f'.{self.bundle} MyTarget',
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit),
                    'platform': self.get_platform(self.is_android),
                    'account': 'MyTarget',
                    'placementid': placements_ids[unit].get('placement_id'),
                    'slotId': placements_ids[unit].get('slot_id'),
                    'appId': app_id,
                    'mark': self.get_mark(unit, is_bid=True),
                    'mediation': MediationTo1cConvertor.convert(self.mediation)
                })
            )

            if unit[0] == 'i':
                is_info['slotId'].update({'inter': placements_ids[unit].get('slot_id')})
                is_info['PlacementID'].update({'inter': placements_ids[unit].get('slot_id')})

            if unit[0] == 'v':
                is_info['slotId'].update({'reward': placements_ids[unit].get('slot_id')})
                is_info['PlacementID'].update({'reward': placements_ids[unit].get('slot_id')})

            if self.mediation == Mediators.MAX.value:
                # ЦЕ ПРАЦЮЄ ТІЛЬКИ ПОКИ В НАС mark = 'Def'!!!!!!
                try:
                    message = MaxMediation(
                        ad_format=MyTargetToMaxConvertor.convert_ad_format(unit),
                        platform=MyTargetToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=self.kids,
                        ad_network=MaxAdNetworks.MyTarget,
                        unit_id=placements_ids[unit].get('slot_id'),
                        app_key=None,
                        app_id=None
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type(unit)}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type(unit)}. '

        data_base_to_send = MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT)

        for info in info_to_send:
            data_base_to_send.send_to_1c(
                ad_service='MyTarget',
                json=info,
                username=self._user_name
            )

        return True, self.message

# print(MyTarget(
#     bundle='net.gameo.roadlimits',
#     is_android=True,
#     ad_format=[AdFormats.banner, AdFormats.inter, AdFormats.reward],
#     categories=[],
#     mediation=Mediators.CAS.value,
#     kids=True
# ).auto_writing())
