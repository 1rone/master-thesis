import requests
import json
from AdServices.AdService import AdService
from AdServices.Mediators.MaxMediation import MaxMediation
from AdServices.Mediators.IronSourceMediation import IronSource
from Convertors.AdColonyToIronSourceConvertor import AdColonyToIronSourceConvertor
from Exceptions.Exceptions import *
from DataBase.MySql import MySql
from Config.config import DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_PORT
from Enums.Enums import AdFormats, MaxAdNetworks, Mediators, IronSourceAdNetworks as IS
from Convertors.AdColonyToMaxConvertor import AdColonyToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor


class AdColony(AdService):
    def __init__(self, bundle: str, coppa: int, ad_format, categories, is_android: bool, mediation: str):
        super().__init__()
        self.bundle = bundle
        self.mediation = mediation
        self.coppa = coppa
        self.ad_format = ad_format
        self.categories = categories
        self.is_android = is_android
        self.message = "Успішно. "
        self.cookies = self.get_header(MySql(host=DB_SENDER_HOST,
                                             user=DB_SENDER_USER,
                                             password=DB_SENDER_PASSWORD,
                                             db=DB_SENDER_NAME,
                                             port=DB_SENDER_PORT).get_headers(ad_service='AdColony',
                                                                              header_name='Cookie'))
        self.x_csrf = self.get_header(MySql(host=DB_SENDER_HOST,
                                            user=DB_SENDER_USER,
                                            password=DB_SENDER_PASSWORD,
                                            db=DB_SENDER_NAME,
                                            port=DB_SENDER_PORT).get_headers(ad_service='AdColony',
                                                                             header_name='X-CSRF-Token'))

    def create_app(self):
        url = 'https://clients.adcolony.com/apps?api=true&v=3.1.3'

        headers = {
            'Content-Type': 'application/json',
        }
        headers.update({**self.cookies, **self.x_csrf})

        data = {
            "platform": "android" if self.is_android else "ios",
            "country": "global",
            "enable_crash_reporting_override": False,
            "audio_option": "on",
            "enable_active_zone_limit": True,
            "name": self.bundle,
            "enable_keywords_coppa": True if self.coppa else False,
            "allow_skip_ads": True if self.coppa else False,
            "skip_ad_time": 6,
            "_isSyncing": True,
            "show_zone_status_bar": False,
            "active_zone_percentage": 100,
            "inactive_zone_count": None,
            "ad_orientation": "landscape"
        }

        data.update({"filters": self.categories})

        req = requests.post(url=url,
                            headers=headers,
                            json=data)

        match req.status_code:
            case 201 | 200:
                app_id = json.loads(req.text).get('result').get('id')
            case 403 | 441:
                raise WrongToken
            case _:
                raise CannotCreateApp

        url = f'https://clients.adcolony.com/apps/{app_id}?api=true&v=3.1.3'

        headers = {
            'Content-Type': 'application/json',
        }

        headers.update(self.cookies)

        req = requests.get(url=url,
                           headers=headers)

        match req.status_code:
            case 200 | 201:
                app_id_1c = json.loads(req.text).get('result').get('uuid')
            case 403:
                raise WrongToken
            case _:
                raise CannotGetAppId

        return {'app_id': app_id,
                'app_id_1c': app_id_1c}

    def create_placement(self, app_id, ad_format):
        url = f'https://clients.adcolony.com/apps/{app_id}/zones?api=true&v=3.1.3'

        headers = {
            'Content-Type': 'application/json'
        }

        headers.update({**self.cookies, **self.x_csrf})

        if ad_format == AdFormats.banner:
            name = 'b.bid'
            data = {
                "app": {
                    "id": app_id
                },
                "active": True,
                "zone_display_format": "banner",
                "house_ad_mode": "backfill",
                "session_play_cap": 0,
                "play_interval": 1,
                "test_ads": False,
                "notes": None,
                "v4vc_daily_max_per_user": 0,
                "zone_type": "interstitial",
                "payment_method": "variable_cpm",
                "enable_prefetch": False,
                "enable_skip_ad_override": True if self.coppa else False,
                "v4vc_enabled": False,
                "client_v4vc_only": False,
                "zone_price_floor_type": "conditional_ecpm",
                "enable_global_default": True,
                "enable_zone_price_floors": True,
                "global_default_payment_model": "variable_cpm",
                "ad_type": "video",
                "iap_ad_mode": "no_iap",
                "campaign_type_filter": "all",
                "creative_type_filter": "all",
                "allow_skip_ads": True if self.coppa else False,
                "skip_ad_time": 6,
                "allow_any_ad_skip_time": False,
                "enable_payment_method_override": True,
                "countryPricings": [],
                "name": name,
                "ad_type_filter_all": True,
                "ad_type_filters": [
                    2,
                    4
                ],
                "daily_play_cap": "0",
                "_isSyncing": True,
                "status": "on"
            }
        elif ad_format == AdFormats.inter:
            name = 'i.bid'
            data = {
                "app": {
                    "id": app_id
                },
                "active": True,
                "zone_display_format": "fullscreen",
                "house_ad_mode": "backfill",
                "session_play_cap": 0,
                "play_interval": 1,
                "test_ads": False,
                "notes": None,
                "v4vc_daily_max_per_user": 0,
                "zone_type": "interstitial",
                "payment_method": "variable_cpm",
                "enable_prefetch": False,
                "enable_skip_ad_override": True,
                "v4vc_enabled": False,
                "client_v4vc_only": False,
                "zone_price_floor_type": "conditional_ecpm",
                "enable_global_default": True,
                "enable_zone_price_floors": False,
                "global_default_payment_model": "variable_cpm",
                "ad_type": "video",
                "iap_ad_mode": "no_iap",
                "campaign_type_filter": "all",
                "creative_type_filter": "all",
                "allow_skip_ads": True,
                "skip_ad_time": 6,
                "allow_any_ad_skip_time": False,
                "enable_payment_method_override": True,
                "countryPricings": [],
                "name": name,
                "anti_client_v4vc_only": True,
                "ad_type_filter_all": True,
                "ad_type_filters": [
                    1,
                    2,
                    4
                ],
                "daily_play_cap": "0",
                "_isSyncing": True,
                "status": "on"
            }
        else:
            name = 'v.bid'
            data = {
                "app": {
                    "id": app_id
                },
                "active": True,
                "zone_display_format": "fullscreen",
                "house_ad_mode": "backfill",
                "session_play_cap": 0,
                "play_interval": 1,
                "test_ads": False,
                "notes": None,
                "v4vc_daily_max_per_user": 0,
                "zone_type": "interstitial",
                "payment_method": "variable_cpm",
                "enable_prefetch": False,
                "enable_skip_ad_override": True if self.coppa else False,
                "v4vc_enabled": True,
                "client_v4vc_only": True,
                "zone_price_floor_type": "conditional_ecpm",
                "enable_global_default": True,
                "enable_zone_price_floors": False,
                "global_default_payment_model": "variable_cpm",
                "ad_type": "video",
                "iap_ad_mode": "no_iap",
                "campaign_type_filter": "all",
                "creative_type_filter": "all",
                "allow_skip_ads": True if self.coppa else False,
                "skip_ad_time": 6,
                "allow_any_ad_skip_time": False,
                "anti_client_v4vc_only": False,
                "enable_payment_method_override": True,
                "countryPricings": [],
                "name": name,
                "v4vc_currency_name": "Credits",
                "v4vc_currency_reward": "1",
                "v4vc_callback_url": None,
                "ad_type_filter_all": True,
                "ad_type_filters": [
                    1,
                    2,
                    4
                ],
                "daily_play_cap": "0",
                "_isSyncing": True,
                "status": "on"
            }

        req = requests.post(
            url=url,
            headers=headers,
            json=data
        )

        match req.status_code:
            case 200 | 201:
                placement_id = json.loads(req.text).get('result').get('id')
            case 401:
                raise WrongToken
            case _:
                raise ProblemsWithPlacementCreation

        url = f'https://clients.adcolony.com/zones/{placement_id}?api=true&v=3.1.3'

        headers = {
            'Content-Type': 'application/json'
        }

        headers.update(self.cookies)

        req = requests.get(url=url,
                           headers=headers)

        match req.status_code:
            case 201 | 200:
                placement_id_1c = json.loads(req.text).get('result').get('uuid')
            case 403:
                raise WrongToken
            case _:
                raise CannotGetPlacementId

        return {name: placement_id_1c}

    def auto_writing(self):
        app = self.create_app()

        placements = {}

        for ad_format in self.ad_format:
            placements.update(self.create_placement(app_id=app['app_id'],
                                                    ad_format=ad_format))

        info_to_send = []

        is_info = {}

        for unit in placements:
            info_to_send.append(
                json.dumps({
                    'name': ('a.' if self.is_android else 'i.') + f'{unit}.{self.bundle} AdColony',
                    'app': self.bundle,
                    'mark': self.get_mark('x.' + unit, is_bid=True),
                    'bannerType': self.get_ad_type('x.' + unit),
                    'platform': self.get_platform(is_android=self.is_android),
                    'account': 'AdColony',
                    'rtb': placements[unit],
                    'appId': app['app_id_1c'],
                    'mediation': MediationTo1cConvertor.convert(self.mediation)
                })
            )

            if unit[0] == 'i':
                is_info['inter'] = placements[unit]

            if unit[0] == 'b':
                is_info['banner'] = placements[unit]

            if unit[0] == 'v':
                is_info['reward'] = placements[unit]

            if self.mediation == Mediators.MAX.value:
                try:
                    message = MaxMediation(
                        ad_format=AdColonyToMaxConvertor.convert_ad_format(unit),
                        platform=AdColonyToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=bool(self.coppa),
                        ad_network=MaxAdNetworks.AdColony,
                        unit_id=placements[unit],
                        app_key=None,
                        app_id=app['app_id_1c']
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type("x." + unit)}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type("x." + unit)}. '

        if self.mediation == Mediators.IS.value:
            try:
                message = IronSource(
                    ad_format=AdColonyToIronSourceConvertor.convert_ad_formats(placements=self.ad_format),
                    bundle=self.bundle,
                    kids=bool(self.coppa),
                    is_android=self.is_android,
                    taxonomy=None,
                    provider_name=IS.AdColony.value,
                    app_config1=app['app_id_1c'],
                    app_config2=None,
                    instances=is_info,
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти. Для активації біддера, пиши в адколоні менеджеру'
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
                ad_service='AdColony',
                json=info,
                username=self._user_name
            )

        return True, self.message


# print(AdColony(ad_format=[AdFormats.inter, AdFormats.banner, AdFormats.reward],
#                bundle='com.movies.sfera',
#                is_android=True,
#                coppa=False,
#                categories=[i + 1 for i in range(40)],
#                mediation=Mediators.IS.value).auto_writing())
