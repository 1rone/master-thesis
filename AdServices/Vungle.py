import json
import requests
from AdServices.AdService import AdService
from AdServices.Mediators.IronSourceMediation import IronSource
from AdServices.Mediators.MaxMediation import MaxMediation
from Convertors.VungleToMaxConvertor import VungleToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Convertors.VungleToIronSourceConvertor import VungleToIronSourceConvertor
from Enums.Enums import AdFormats, Mediators, MaxAdNetworks, IronSourceAdNetworks as IS
from DataBase.MySql import MySql
from AdServices.PlacementsId.VunglePlacementsId import VunglePlacements
from Config.config import VUNGLE_KIDS_LOGIN, VUNGLE_ADULTS_LOGIN, VUNGLE_ADULTS_PASSWORD, VUNGLE_KIDS_PASSWORD, \
    VUNGLE_ACCOUNT_ID_KIDS, VUNGLE_ACCOUNT_ID_ADULTS, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import *


class Vungle(AdService):
    def __init__(self, kids, is_android, bundle, ad_format, mediation):
        super().__init__()
        self.kids = kids
        self.mediation = mediation
        if self.kids:
            self.token = self.get_token(login=VUNGLE_KIDS_LOGIN, password=VUNGLE_KIDS_PASSWORD)
        else:
            self.token = self.get_token(login=VUNGLE_ADULTS_LOGIN, password=VUNGLE_ADULTS_PASSWORD)
        self.is_android = is_android
        self.bundle = bundle
        self.ad_format = ad_format
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.message = 'Успішно. '
        self.accountID = VUNGLE_ACCOUNT_ID_KIDS if self.kids else VUNGLE_ACCOUNT_ID_ADULTS

    @staticmethod
    def get_token(login, password):
        url = 'https://auth-api.vungle.com/login'

        headers = {
            'accept': 'application/json',
            'vungle-source': 'api',
            'vungle-version': '1',
            'Content-Type': 'application/json'
        }

        data = {
            "username": login,
            "password": password
        }

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        match req.status_code:
            case 200:
                return json.loads(req.text).get('token')
            case _:
                raise CannotGetToken

    def create_app(self):
        url = 'https://publisher-api.vungle.com/api/v1/applications'

        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        data = {
            "platform": "android" if self.is_android else "ios",
            # "name": self.bundle + 'delete_me_34',
            "name": self.bundle,
            "store": {
                "id": self.bundle,
                "url": self.link,
                "category": "Games",

            },
            "isCoppa": True if self.kids else False}

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        match req.status_code:
            case 409:
                raise AlreadyCreatedApp
            case 400:
                if 'check market id err' in req.text:
                    raise CannotFindApp
                else:
                    print(f'req.status_code={req.status_code}',
                          req.text)
                    raise Exception
            case 200:
                return json.loads(req.text).get('id'), json.loads(req.text).get('defaultPlacement')
            case _:
                print(f'req.status_code={req.status_code}',
                      req.text)
                raise Exception

    def create_placement(self, app_id, ad_format, price, name):

        url = 'https://publisher-api.vungle.com/api/v1/placements'

        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        data = {
            "application": app_id,
            "name": name,
            "type": "interstitial" if ad_format == AdFormats.inter else
            'rewarded' if ad_format == AdFormats.reward else 'banner',
            "allowEndCards": True if ad_format != AdFormats.banner else False,
            "isSkippable": True if self.kids else True if ad_format == AdFormats.inter else False,
            "banner": {
                "adRefreshDuration": 30,
                "isRefreshEnabled": False
            }
        }

        if 'bid' in name:
            data.update({"isHBParticipation": True})
        else:
            data.update({
                "flatCPM": {
                    "default": float(price)
                },
                "isFlatCPMEnabled": True,
            })

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(data))

        print(f'Створив {ad_format} з назвою: {name}')

        match req.status_code:
            case 200:
                return json.loads(req.text).get('referenceID')
            case _:
                print(f'req.status_code={req.status_code}',
                      req.text)
                raise Exception

    def activate_app(self, app_id):
        url = f'https://publisher-api.vungle.com/api/v1/applications/{app_id}'

        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        data = {
            # "name": self.bundle + 'delete_me_34',
            "name": self.bundle,
            "status": "active",
            "forceView": {
                "rewarded": False if self.kids else True,
                "nonRewarded": False},
            "maxVideoLength": 30 if self.kids else 45
        }

        req = requests.patch(url=url,
                             headers=headers,
                             data=json.dumps(data))

        match req.status_code:
            case 200:
                return True
            case _:
                print(f'req.status_code={req.status_code}',
                      req.text)
                raise Exception

    def archive_default_placement(self, placement_id):

        url = f'https://publisher-api.vungle.com/api/v1/placements/{placement_id}'

        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        data = {
            "name": "default",
            "status": "inactive"
        }

        req = requests.patch(url=url,
                             headers=headers,
                             data=json.dumps(data))

        if req.status_code == 200:
            return True

        return False

    def auto_writing(self):

        app_id, default_placement_id = self.create_app()
        placements_ids_names = {}

        vungle_placements = VunglePlacements()

        for ad_format in self.ad_format:
            match ad_format:
                case AdFormats.banner:
                    placements = vungle_placements.get_banner()
                case AdFormats.inter:
                    placements = vungle_placements.get_interstitial()
                case AdFormats.reward:
                    placements = vungle_placements.get_rewarded()
                case _:
                    raise WrongPlacementTypeException
            for placement in placements:
                placements_ids_names[self.create_placement(app_id=app_id,
                                                           ad_format=ad_format,
                                                           name=placement,
                                                           price=placement[2:])] = placements[placement]

        self.activate_app(app_id=app_id)

        self.archive_default_placement(placement_id=default_placement_id)

        info_to_send = []

        is_info = {}

        for unit in placements_ids_names:
            info_to_send.append(
                json.dumps({
                    'name': ('a.' if self.is_android else 'i.') + f'{placements_ids_names[unit]}{self.bundle} '
                                                                  f'' + ('Vungle' if self.kids else 'Vungle 2'),
                    'app': self.bundle,
                    'mark': self.get_mark(placements_ids_names[unit], is_bid=True),
                    'bannerType': self.get_ad_type('x.' + placements_ids_names[unit]),
                    'platform': self.get_platform(is_android=self.is_android),
                    'account': 'Vungle' if self.kids else 'Vungle 2',
                    'id': unit,
                    'appId': app_id,
                    'mediation': MediationTo1cConvertor.convert(self.mediation) if self.get_mark(
                        placements_ids_names[unit]) in ['Def', 'Bid'] else '',
                    'Accountid': self.accountID if self.mediation == Mediators.CAS.value else ''
                })
            )

            if placements_ids_names[unit][0] == 'i':
                is_info['inter'] = unit

            if placements_ids_names[unit][0] == 'b':
                is_info['banner'] = unit

            if placements_ids_names[unit][0] == 'v':
                is_info['reward'] = unit

            if self.mediation == Mediators.MAX.value:

                # if self.get_mark(placements_ids_names[unit], is_bid=True) in ['Def', 'x5.00']:

                try:
                    message = MaxMediation(
                        ad_format=VungleToMaxConvertor.convert_ad_format(placements_ids_names[unit]),
                        platform=VungleToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=self.kids,
                        ad_network=MaxAdNetworks.Vungle,
                        unit_id=unit,
                        app_key=None,
                        app_id=app_id
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type("x." + placements_ids_names[unit])}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type("x." + placements_ids_names[unit])}. '

        if self.mediation == Mediators.IS.value:
            try:
                message = IronSource(
                    ad_format=VungleToIronSourceConvertor.convert_ad_formats(placements=self.ad_format),
                    bundle=self.bundle,
                    kids=self.kids,
                    is_android=self.is_android,
                    taxonomy=None,
                    provider_name=IS.Vungle.value,
                    app_config1=app_id,
                    app_config2=app_id,
                    instances=is_info
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти.'
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
                ad_service='Vungle' if self.kids else 'Vungle 2',
                json=info,
                username=self._user_name
            )

        return True, self.message


# print(Vungle(kids=False,
#              ad_format=[AdFormats.banner, AdFormats.inter, AdFormats.reward],
#              is_android=True,
#              bundle='com.smoqgames.packopen22',
#              mediation=Mediators.IS.value).auto_writing())
