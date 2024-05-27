import json
import requests
import traceback
from AdServices.AdService import AdService
from AdServices.Mediators.IronSourceMediation import IronSource
from AdServices.Mediators.MaxMediation import MaxMediation
from Convertors.TapJoyToMaxConvertor import TapJoyToMaxConvertor
from Convertors.TapJoyToIronSourceConvertor import TapJoyToIronSourceConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Enums.Enums import AdFormats, Mediators, MaxAdNetworks, TapjoyMaturity, IronSourceAdNetworks as IS
from DataBase.MySql import MySql
from Config.config import DB_SENDER_HOST, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_USER, DB_SENDER_PORT
from Exceptions.Exceptions import *


class TapJoy(AdService):

    def __init__(self,
                 is_android: bool,
                 bundle: str,
                 orientation: str,
                 ad_format: [str],
                 maturity: int,
                 mediation: str,
                 categories: []):
        super().__init__()
        self.is_android = is_android
        self.bundle = bundle
        self.orientation = orientation
        headers_db = MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT)
        self.mediation = mediation
        self.message = 'Успішно. '
        self.cookie = self.get_header(headers_db.get_headers(ad_service='TapJoy', header_name='Cookie'))
        self.token = self.get_header(headers_db.get_headers(ad_service='TapJoy', header_name='X-CSRFToken'))
        if AdFormats.banner in ad_format:
            ad_format.remove(AdFormats.banner)
        if not ad_format:
            raise NoAdFormats
        self.ad_format = ad_format
        self.maturity = maturity
        self.categories = categories

    def get_placements_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Host': 'dashboard.tapjoy.com',
            'Origin': 'https://ltv.tapjoy.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Connection': 'keep-alive',
            'Referer': 'https://ltv.tapjoy.com/',
            'X-Fiverocks-Client': 'Spirra'
        }

        headers.update(self.cookie)

        return headers

    def create_app(self):
        url = 'https://ltv.tapjoy.com/d/app_groups'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'ltv.tapjoy.com',
            'Origin': 'https://ltv.tapjoy.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Referer': 'https://ltv.tapjoy.com/s/create_app',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Fiverocks-Client': 'Spirra',
        }

        data = {
            "name": self.bundle,
            "display_timezone": "Etc/UTC",
            "currency": "USD",
            "coppa_approach": "sdk_flag",
            "android": True if self.is_android else False,
            "iphone": False if self.is_android else True,
            "landscape": True if self.orientation == 'landscape' or self.orientation == 'both' else False,
            "portrait": True if self.orientation == 'portrait' or self.orientation == 'both' else False,
            "mediation": True,
        }

        data.update({
                        "android_store_id": self.bundle,
                        "android_store_country": ""
                    } if self.is_android else {
            "iphone_store_id": self.bundle,
            "iphone_store_country": ""
        })

        headers.update({**self.cookie, **self.token})

        req = requests.post(url=url,
                            headers=headers,
                            json=data)

        if req.status_code == 201:
            return {
                'sdk_api_key': json.loads(req.text).get('platforms')[0].get('sdk_api_key'),
                'app_group_id': json.loads(req.text).get('app_group_id'),
                'time': json.loads(req.text).get('created_at'),
                'app_id': json.loads(req.text).get('platforms')[0].get('id')

            }

        elif req.status_code == 200:
            raise WrongToken

        else:
            print('status code=', req.status_code)
            print('text=', req.text)
            print(traceback.format_exc())
            raise Exception

    def create_currency(self, app_id, maturity, categories):

        def get_body() -> str:
            body = 'currency%5Binitial_balance%5D=5&' \
                   'currency%5Bconversion_rate%5D=1&' \
                   'currency%5Bname%5D=Coins&___' \
                   'currency%5Bsecret_key%5D=D683upURce3ztJQ0Wsws&' \
                   'currency%5Bcallback_url%5D=TAP_POINTS_CURRENCY&' \
                   'currency%5Ballow_real_world_exchange_description%5D=&' \
                   f'currency%5Bmax_age_rating%5D={maturity}&' \
                   'currency%5Ballow_real_world_exchange%5D=false&' \
                   'currency%5Bdescription%5D=coin&' \
                   'currency%5Bco_registration_disabled%5D=false'

            mature = ''
            if maturity == TapjoyMaturity.Mature.value:
                for i in categories:
                    mature += f'currency%5Bmature_rating_array%5D%5B%5D={i}&'
                body.replace('___', mature)

            return body

        url = f'https://dashboard.tapjoy.com/api/client/apps/{app_id}/currencies'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Host': 'dashboard.tapjoy.com',
            'Origin': 'https://ltv.tapjoy.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
            'Connection': 'keep-alive',
            'Referer': 'https://ltv.tapjoy.com/',
            'X-Fiverocks-Client': 'Spirra'
        }

        headers.update(self.cookie)

        req = requests.post(url=url,
                            headers=headers,
                            data=get_body())

        answer = {
            'id': json.loads(req.text).get('result').get('currency').get('id'),
            'time': json.loads(req.text).get('result').get('currency').get('created_at')
        }

        if req.status_code == 200:
            return answer

        else:
            print('status code=', req.status_code)
            print('text=', req.text)
            print(traceback.format_exc())
            raise Exception

    def create_placement(self, app_id, app_group_id, ad_format):
        url = f'https://dashboard.tapjoy.com/api/client/publisher/app_groups/{app_group_id}/placements'

        headers = self.get_placements_headers()

        data = {"placement_type": "contextual",
                "name": ('a.' if self.is_android else 'i.') + (
                    'i.bid.' if ad_format == AdFormats.inter else 'v.bid.') + app_id.replace('-', ''),
                "category": "user_pause",
                "mediation_name": "max" if self.mediation == Mediators.MAX.value else "ironsource"
                if self.mediation == Mediators.IS.value else "Mediated"}

        req = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )

        if req.status_code == 201:
            return json.loads(req.text).get('id')

        else:
            print('status code=', req.status_code)
            print('text=', req.text)
            print(traceback.format_exc())
            raise Exception

    def fulfill_placement(self, app_id, ad_format, placement_id, created_time, currency_id):
        url = f'https://dashboard.tapjoy.com/api/client/publisher/apps/{app_id}/actions'

        headers = self.get_placements_headers()

        name = ('a.' if self.is_android else 'i.') + \
               ('i.bid.' if ad_format == AdFormats.inter else 'v.bid.') + app_id.replace('-', '')

        data = {"video_autoplay_timer": 0, "autoplay_video": True, "hide_video_close_button": True,
                "confirm_content_close": True if ad_format == AdFormats.inter else False, "close_button_timeout": 5,
                "tiered_exchange_rate_multipliers": None, "tiered_exchange_rate_standalone_multipliers": None,
                "reward_amt": 0, "rewarding": "fixed", "exchange_rate_multiplier": None, "exchange_rate_rules": None,
                "placement_ids": [placement_id], "segment_ids": [], "target": "all",
                "enabled": True, "from_when": created_time, "until_when": None, "impression_total": "",
                "impression_interval": "", "impression_interval_unit": "day", "source_type": "ad", "mediation": {},
                "ow_ab_test": None, "ow_ab_test_enabled": False, "owConfiguration": None,
                "name": name,
                "currency_id": currency_id, "app_id": app_id,
                "ad_type": "programmatic_fsi" if ad_format == AdFormats.inter else "programmatic_direct_play"}

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        if req.status_code == 201:
            return name

        else:
            print('status code=', req.status_code)
            print('text=', req.text)
            print(traceback.format_exc())
            raise Exception

    def auto_writing(self):
        app_info = self.create_app()

        cur_info = self.create_currency(app_id=app_info.get('app_id'),
                                        maturity=self.maturity,
                                        categories=self.categories)

        info = []

        for ad_format in self.ad_format:
            info.append(self.fulfill_placement(app_id=app_info.get('app_id'),
                                               ad_format=ad_format,
                                               placement_id=self.create_placement(app_group_id=app_info['app_group_id'],
                                                                                  ad_format=ad_format,
                                                                                  app_id=app_info.get('app_id')),
                                               created_time=cur_info.get('time'),
                                               currency_id=cur_info.get('id')))

        info_to_send = []

        is_info = {}

        for unit in info:
            info_to_send.append(
                json.dumps({
                    'name': unit + ' Tapjoy',
                    'appId': app_info.get('sdk_api_key'),
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit),
                    'platform': self.get_platform(self.is_android),
                    'account': 'Tapjoy',
                    'rtb': unit,
                    'mark': self.get_mark(unit, is_bid=True),
                    'mediation': MediationTo1cConvertor.convert(self.mediation)
                })
            )
            #  перевірити чи закоментоване діє так само як 3-и іф'а під ним. якщо так — замінити
            #  is_info['inter'] = unit if unit[2] == 'i' else is_info['banner'] = unit if unit[2] == 'b' else is_info['reward'] = unit

            if unit[2] == 'i':
                is_info['inter'] = unit

            if unit[2] == 'b':
                is_info['banner'] = unit

            if unit[2] == 'v':
                is_info['reward'] = unit

            if self.mediation == Mediators.MAX.value:
                # ЦЕ ПРАЦЮЄ ТІЛЬКИ ПОКИ В НАС mark = 'Def'!!!!!!
                try:
                    message = MaxMediation(
                        ad_format=TapJoyToMaxConvertor.convert_ad_format(unit),
                        platform=TapJoyToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=TapJoyToMaxConvertor.convert_maturity(maturity=self.maturity),
                        ad_network=MaxAdNetworks.TapJoy,
                        unit_id=unit,
                        app_key=None,
                        app_id=app_info.get('sdk_api_key')
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type(unit)}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type(unit)}. '

        if self.mediation == Mediators.IS.value:
            try:
                message = IronSource(
                    ad_format=TapJoyToIronSourceConvertor.convert_ad_formats(placements=self.ad_format),
                    bundle=self.bundle,
                    kids=TapJoyToIronSourceConvertor.convert_maturity(self.maturity),
                    is_android=self.is_android,
                    taxonomy=None,
                    provider_name=IS.TapJoy,
                    app_config={
                        'sdkKey': app_info.get('sdk_api_key'),
                        'apiKey': 'c49aaccd-116b-4d42-8fc8-470aa685a7ec'},
                    instance_config={'placementName': is_info}
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти. Для активації біддера, виконай типові дії'
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
                ad_service='Tapjoy',
                json=info,
                username=self._user_name
            )

        return True, self.message

# print(TapJoy(
#     bundle='net.gameo.roadlimits',
#     is_android=True,
#     orientation='both',
#     ad_format=[AdFormats.inter, AdFormats.banner, AdFormats.reward],
#     maturity=2,
#     categories=[1, 2, 4, 16],
#     mediation=Mediators.IS.value
# ).auto_writing())
