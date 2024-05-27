import requests
import json
from AdServices.PlacementsId.DTExchangePlacementsId import DTExchangePlacementsKids, DTExchangePlacementsAdults
from Exceptions.Exceptions import *
from AdServices.AdService import AdService
from DataBase.MySql import MySql
from Config.config import DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_HOST, DB_SENDER_NAME, DB_SENDER_PORT
from Enums.Enums import AdFormats


def get_placement_name(is_android, template):
    if is_android:
        answer = 'a.' + template
    else:
        answer = 'i.' + template
    return answer


class DTExchange(AdService):

    def __init__(self, bundle, ad_formats, kids, is_android):
        super().__init__()
        self.bundle = bundle
        self.ad_formats = ad_formats
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.kids = kids
        self.coppa = True if self.kids else False
        self.cookie = self.get_header(MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT).get_headers(ad_service='DTExchange',
                                             header_name='Cookie'))
        self.placements = self.get_placements()
        self.mediation = 'CAS'
        self.is_android = is_android

    @staticmethod
    def get_ad_type(placement_id) -> str:
        match placement_id[0]:
            case 'i':
                return AdFormats.inter
            case 'v':
                return AdFormats.reward
            case _:
                return AdFormats.banner

    @staticmethod
    def get_price(placement):
        return float(placement[2:])

    def get_placements(self):
        my_class = DTExchangePlacementsKids() if self.kids else DTExchangePlacementsAdults()
        template = {}
        if AdFormats.banner in self.ad_formats:
            template.update(**my_class.get_banner())
        if AdFormats.inter in self.ad_formats:
            template.update(**my_class.get_interstitial())
        if AdFormats.reward in self.ad_formats:
            template.update(**my_class.get_rewarded())
        return template

    def get_app_info(self):
        url = f'https://console.fyber.com/api/v2/store/search-apps?q={self.bundle}&storeType=all'

        headers = {
            'Host': 'console.fyber.com'
        }

        headers.update(self.cookie)

        req = requests.get(url=url,
                           headers=headers)

        match req.status_code:
            case 401:
                raise WrongToken
            case 200:
                for app in json.loads(req.text):
                    if str(app.get('bundle')) != self.bundle:
                        continue
                    else:
                        cor_app = app
                        break
                else:
                    raise CannotFindApp

                answer = {
                    'category1': cor_app.get('category1'),
                    'category2': cor_app.get('category2'),
                    'imageUrl': cor_app.get('imageUrl')
                }
            case _:
                raise CannotFindApp

        return answer

    def create_app(self):
        app_info = self.get_app_info()

        url = 'https://console.fyber.com/api/v2/app/add-app'

        headers = {
            'Host': 'console.fyber.com'
        }
        headers.update(self.cookie)

        data = {
            "name": self.bundle,
            "coppa": self.coppa,
            "platform": "android" if self.is_android else "ios",
            "generic": False,
            "category1": app_info['category1'],
            "category2": app_info['category2'],
            "imageUrl": app_info['imageUrl'],
            "bundle": self.bundle,
            "storeType": "google" if self.is_android else "apple",
            "storeUrl": self.link,
            "placementTypesToAdd": []
        }

        req = requests.post(
            url=url,
            headers=headers,
            json=data
        )

        match req.status_code:
            case 200:
                return json.loads(req.text).get('id')
            case 400:
                if 'App with such a name' in req.text:
                    raise AlreadyCreatedApp
                else:
                    raise CannotCreateApp
            case _:
                raise CannotCreateApp

    def create_placement(self, app_id, ad_format, placement_name, price):

        def get_creative_types():
            if ad_format == AdFormats.banner:
                return [{
                    "id": "4",
                    "name": "Banner",
                    "format": "static",
                    "unitFormatsIDs": [
                        "Display"
                    ]
                }]
            elif ad_format == AdFormats.inter:
                return [
                    {
                        "id": "2",
                        "name": "Display",
                        "format": "static",
                        "unitFormatsIDs": [
                            "Display",
                            "VideoAndDisplay"
                        ]
                    },
                    {
                        "id": "1",
                        "name": "Video",
                        "format": "video",
                        "unitFormatsIDs": [
                            "Video",
                            "VideoAndDisplay"
                        ]
                    }
                ]
            elif ad_format == AdFormats.reward:
                return [
                    {
                        "id": "3",
                        "name": "Rewarded Video",
                        "format": "video",
                        "unitFormatsIDs": [
                            "VideoAndDisplay"
                        ]
                    },
                    {
                        "id": "2",
                        "name": "Display",
                        "format": "static",
                        "unitFormatsIDs": [
                            "Display",
                            "VideoAndDisplay"
                        ]
                    }
                ]
            else:
                raise WrongPlacementTypeException

        def get_placement_type():
            answer = {
                AdFormats.banner: '1',
                AdFormats.inter: '2',
                AdFormats.reward: '3'
            }
            return answer[ad_format]

        url = 'https://console.fyber.com/api/v2/placements/add-placement'

        headers = {
            'Host': 'console.fyber.com'
        }
        headers.update(self.cookie)

        data = {
            "spot": {
                "id": "",
                "name": placement_name,
                "appId": app_id,
                "app": None,
                "units": [],
                "placementType": get_placement_type(),
                "creativeTypes": get_creative_types(),
                "status": "unknown",
                "rewardedConfig": {
                    "id": "",
                    "currency": {
                        "id": "",
                        "appId": "",
                        "currency": ""
                    },
                    "amount": 0,
                    "rewardingType": "client",
                    "placementId": ""
                },
                "placementPerformance": {
                    "publisherId": "",
                    "appId": "",
                    "placementId": "",
                    "publisherNet": 0,
                    "impressions": 0,
                    "fillRate": 0,
                    "ecpm": 0,
                    "engagementRate": 0,
                    "frequency": 0,
                    "placementPerformanceReporting": {
                        "publisherId": "",
                        "appId": "",
                        "placementId": "",
                        "avgLatency": 0
                    }
                }
            },
            "floorPrices": [
                {"_initValue": price, "value": price, "dirty": False, "$": price, "hasBeenValidated": False,
                 "_autoValidationDefault": True,
                 "_autoValidationEnabled": False, "lastValidationRequest": 0, "preventNextQueuedValidation": False,
                 "validating": False, "focused": False, "touched": False, "submitted": False,
                 "_validators": [None, None, None],
                 "validationPromise": None, "country": {"code": "WW", "country": "Worldwide"}}
            ]
        }

        req = requests.post(
            url=url,
            headers=headers,
            json=data
        )

        match req.status_code:
            case 200:
                for unit in json.loads(req.text).get('units'):
                    if unit['name'] == placement_name:
                        placement = unit
                        break
                else:
                    raise CannotGetPlacementId
            case _:
                raise ProblemsWithPlacementCreation

        if ad_format == AdFormats.banner:
            url = 'https://console.fyber.com/api/v2/unit'

            data = {
                "id": placement['id'],
                "name": placement_name,
                "spotId": placement['spotId'],
                "status": "active",
                "contentName": placement['contentName'],
                "fullName": placement['fullName'],
                "spot": None,
                "coppa": self.coppa,
                "floorPrices": [
                    {
                        "value": price,
                        "country": {
                            "code": "WW",
                            "country": "Worldwide"
                        }
                    }
                ],
                "floorPriceRange": {
                    "min": 0.01,
                    "max": 0.01,
                    "entityId": ""
                },
                "unitType": "banner",
                "format": "Display",
                "freq": 100,
                "config": {
                    "track": [
                        "errors"
                    ],
                    "vendor": [],
                    "filteredAPIs": [],
                    "fullScreen": False,
                    "battr": [
                        3,
                        6,
                        7,
                        9,
                        10,
                        13,
                        14,
                        17
                    ]
                },
                "tpnConfigs": [],
                "mediationConfig": {
                    "capping": {
                        "id": "freq_2_0",
                        "unit": "2",
                        "value": 0,
                        "enabled": False
                    },
                    "pacing": {
                        "id": "freq_3_1",
                        "unit": "3",
                        "value": 1,
                        "enabled": False
                    },
                    "geo": {
                        "countries": [],
                        "include": True
                    },
                    "connectivity": [],
                    "advertiserTracking": [],
                    "targetingEnabled": False
                },
                "filteredAPIs": [],
                "filteredProtocols": [],
                "skippability": "NotConfigured",
                "bannerRefresh": 120,
                "directSold": False,
                "crossPromo": False
            }

            requests.put(
                url=url,
                headers=headers,
                json=data
            )

        return [placement_name, placement['spotId']]

    def auto_writing(self):
        app_id = self.create_app()
        placements = []
        for placement in self.placements:
            placements.append(self.create_placement(ad_format=self.get_ad_type(placement),
                                                    app_id=app_id,
                                                    placement_name=get_placement_name(is_android=self.is_android,
                                                                                      template=placement),
                                                    price=DTExchange.get_price(placement=placement)))

        info_to_send = []

        for unit in placements:
            info_to_send.append(
                json.dumps({
                    'name': unit[0] + f'.{self.bundle} DT Exchange',
                    'app': self.bundle,
                    'bannerType': AdService.get_ad_type(unit[0]),
                    'platform': self.get_platform(self.is_android),
                    'account': 'DT Exchange',
                    'id': unit[1],
                    'appId': app_id,
                    'mark': self.get_mark((unit[0][2:] + '.'), False),
                    'mediation': ''
                    # 'mediation': MediationTo1cConvertor.convert(self.mediation)
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
                ad_service='DT Exchange',
                json=info,
                username=self._user_name
            )

        return True


# DTExchange(bundle='com.EvolveGames.MinesweeperGo',
#            ad_formats=[AdFormats.inter, AdFormats.banner, AdFormats.reward],
#            kids=True,
#            is_android=True).auto_writing()
