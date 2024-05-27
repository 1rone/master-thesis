from AdServices.Mediators.Mediation import Mediation
from AppInfoGetter import AppInfoGetter
from DataBase.MySql import MySql
from Config.config import MAX_KIDS_TOKEN, MAX_ADULTS_TOKEN, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
import requests
import json
from Exceptions.Exceptions import *
from AdServices.Mediators.MaxAdNetworksInfo import MaxAdNetworksInfo
from Enums.Enums import MaxAdNetworks, MaxPlatforms, MaxAdFormats


def get_ad_unit_name(ad_format):
    match ad_format:
        case 'BANNER':
            return 'banner'
        case 'INTER':
            return 'inter'
        case 'REWARD':
            return 'reward'
        case _:
            raise WrongPlacementNameException


def convert_ad_type(ad_format) -> str:
    return 'interstitial' if ad_format == MaxAdFormats.INTER.name else \
        'rewarded' if ad_format == MaxAdFormats.REWARD.name else 'banner'


def convert_platform(platform) -> str:
    return 'Android' if platform == MaxPlatforms.android.name else 'iOS'


def convert_name(platform, ad_format, bundle, kids):
    if platform == MaxPlatforms.android.name:
        name = 'a.'
    else:
        name = 'i.'
    if ad_format == MaxAdFormats.INTER.name:
        name += 'i.bid.'
    elif ad_format == MaxAdFormats.REWARD.name:
        name += 'v.bid.'
    else:
        name += 'b.bid.'
    name += bundle + ' '
    if kids:
        name += 'MAX'
    else:
        name += 'MAX 2'
    return name


class MaxMediation(Mediation):

    def __init__(self,
                 kids: bool,
                 platform: MaxPlatforms,
                 bundle: str,
                 ad_format: MaxAdFormats,
                 ad_network: MaxAdNetworks,
                 unit_id: str | None,
                 app_id: str | None,
                 app_key: str | None,
                 ad_network_optional_placement_id: str | None = None) -> None:
        super().__init__()
        if platform == MaxPlatforms.ios:
            self.bundle = AppInfoGetter.get_info(bundle=bundle).get('ios_package_id')
        else:
            self.bundle = bundle
        self.bundle_for_1c = bundle
        self.kids = kids
        self.platform = platform.name
        self.ad_format = ad_format.name
        self.mediation = 'MAX'
        self.headers = {'Api-key': MAX_KIDS_TOKEN if self.kids else MAX_ADULTS_TOKEN}
        self.db = MySql(host=DB_SENDER_HOST,
                        db=DB_SENDER_NAME,
                        user=DB_SENDER_USER,
                        password=DB_SENDER_PASSWORD,
                        port=DB_SENDER_PORT)
        self.ad_network = ad_network
        self.unit_id = unit_id
        self.app_id = app_id
        self.app_key = app_key
        self.ad_network_optional_placement_id = ad_network_optional_placement_id

    def create_placement(self):
        
        # if self.db.get_mediation_info(mediation=self.mediation,
        #                               bundle=self.bundle,
        #                               banner_type=get_ad_unit_name(self.ad_format)):
        #     raise AlreadyCreatedApp

        url = 'https://o.applovin.com/mediation/v1/ad_unit'

        answer = {}

        data = {
            "name": get_ad_unit_name(ad_format=self.ad_format),
            "platform": self.platform,
            "package_name": self.bundle,
            "ad_format": self.ad_format
        }

        req = requests.post(
            url=url,
            headers=self.headers,
            json=data
        )

        match req.status_code:
            case 403:
                raise InAnotherMediation
            case 400:
                raise AlreadyCreatedPlacement
            case 200 | 201:
                answer[req.json().get('name')] = {
                    'myBundle': self.bundle_for_1c,
                    'mediationBundle': req.json().get("package_name"),
                    'PlacementId': req.json().get('id'),
                    'mediationName': 'MAX'
                }
            case _:
                raise ProblemsWithPlacementCreation

        self.db.send_mediation_info(answer)

        info = json.dumps({
            'name': convert_name(platform=self.platform,
                                 ad_format=self.ad_format,
                                 bundle=self.bundle_for_1c,
                                 kids=self.kids),
            'app': self.bundle_for_1c,
            'mark': 'Bid',
            'bannerType': convert_ad_type(self.ad_format),
            'platform': convert_platform(self.platform),
            'account': 'MAX kids' if self.kids else 'MAX adult',
            'rtb': req.json().get('id'),
            'mediation': 'max'
        })

        self.db.send_to_1c(
            json=info,
            username=self._user_name,
            ad_service='MAX kids' if self.kids else 'MAX adult'

        )

        return True

    def full_fill_placement(self, app_id=None, unit_id=None, app_key=None, ad_network_optional_placement_id=None):

        def get_network_settings():

            def delete_none(_dict):
                """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
                if isinstance(_dict, dict):
                    for key, value in list(_dict.items()):
                        if isinstance(value, (list, dict, tuple, set)):
                            _dict[key] = delete_none(value)
                        elif value is None or key is None:
                            del _dict[key]

                elif isinstance(_dict, (list, set, tuple)):
                    _dict = type(_dict)(delete_none(item) for item in _dict if item is not None)

                return _dict

            answer = {
                network_settings.get('Api Name'): {
                    "disabled": False,
                    "ad_network_app_id": network_settings.get('ad_network_app_id'),
                    "ad_network_app_key": network_settings.get('ad_network_app_key'),
                    "ad_network_ad_units": ([{"ad_network_ad_unit_id": network_settings.get(
                        'ad_network_ad_unit_id')}] if network_settings.get(
                        'ad_network_ad_unit_id') else [])
                }
            }

            if ad_network_optional_placement_id:
                answer[network_settings.get('Api Name')]["extraParameters"] = {
                    "ad_network_optional_placement_id": ad_network_optional_placement_id}

            return delete_none(answer)

        rows = self.db.get_mediation_info(mediation=self.mediation,
                                          bundle=self.bundle,
                                          banner_type=get_ad_unit_name(self.ad_format))
        network_settings = MaxAdNetworksInfo(self.ad_network).get_mediation_info(
            unit_id=unit_id,
            app_id=app_id,
            app_key=app_key)

        for row in rows:
            url = 'https://o.applovin.com/mediation/v1/ad_unit/' + row.get('PlacementId')

            data = {
                "id": row.get('PlacementId'),
                "name": row.get('BannerType'),
                "platform": self.platform,
                "ad_format": row.get('BannerType').upper(),
                "package_name": row.get('MediationBundle'),
                "ad_network_settings": [
                    get_network_settings()
                ]
            }

            req = requests.post(url=url,
                                headers=self.headers,
                                json=data)

            match req.status_code:
                case 200 | 201:
                    return True
                case _:
                    raise CannotFullFillPlacement

    def add_mediation(self) -> str | None:
        if self.db.get_mediation_info(mediation=self.mediation,
                                      bundle=self.bundle,
                                      banner_type=get_ad_unit_name(self.ad_format)):
            self.full_fill_placement(app_id=self.app_id,
                                     app_key=self.app_key,
                                     unit_id=self.unit_id,
                                     ad_network_optional_placement_id=self.ad_network_optional_placement_id)

        else:
            self.create_placement()
            self.full_fill_placement(app_id=self.app_id,
                                     app_key=self.app_key,
                                     unit_id=self.unit_id,
                                     ad_network_optional_placement_id=self.ad_network_optional_placement_id)
            if self.kids:
                return 'Потрібно включити в MAX AdFiltering. '

# MaxMediation(
#     ad_format=MaxAdFormats.BANNER,
#     platform=MaxPlatforms.ios,
#     bundle='1640670179',
#     kids=True,
#     ad_network=MaxAdNetworks.Inmobi,
#     app_id='1664489768466',
#     app_key=None,
#     unit_id='1666295734973',
# ).add_mediation()


# MaxMediation(
#     ad_format=MaxAdFormats.BANNER,
#     platform=MaxPlatforms.ios,
#     bundle='1641111216',
#     kids=True,
#     ad_network=MaxAdNetworks.Inmobi,
#     app_id='1664489768466',
#     app_key=None,
#     unit_id='1666295734973'
# ).create_placement()
