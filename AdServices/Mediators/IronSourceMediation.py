import json
from AdServices.Mediators.Mediation import Mediation
from Exceptions.Exceptions import *
import requests
from DataBase.MySql import MySql
from Config.config import DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_PORT, \
    DB_SENDER_NAME, IRONSOURCE_ADULTS_SECRET, IRONSOURCE_ADULTS_REFRESH, IRONSOURCE_KIDS_REFRESH, IRONSOURCE_KIDS_SECRET
from Enums.Enums import IronSourceAdFormats, AdFormats1C
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Convertors.InputToIronSourceConvertor import InputToIronSourceConvertor
from Convertors.BaseToISConvertor import BaseToISConvertor


class IronSource(Mediation):

    def __init__(self, bundle,
                 is_android,
                 kids,
                 taxonomy,
                 ad_format,
                 provider_name=None,
                 instances=None,
                 app_config1=None,
                 app_config2=None
                 ):
        super().__init__()
        self.db = MySql(host=DB_SENDER_HOST,
                        db=DB_SENDER_NAME,
                        user=DB_SENDER_USER,
                        password=DB_SENDER_PASSWORD,
                        port=DB_SENDER_PORT)
        self.secret = IRONSOURCE_KIDS_SECRET if kids else IRONSOURCE_ADULTS_SECRET
        self.refresh = IRONSOURCE_KIDS_REFRESH if kids else IRONSOURCE_ADULTS_REFRESH
        self.bundle = bundle
        self.is_android = is_android
        self.kids = kids
        self.mediation = 'IS'
        self.taxonomy = taxonomy
        self.ad_format = InputToIronSourceConvertor.convert_ad_formats(ad_format)
        self.token = self.get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}'
        }
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.provider_name = provider_name
        self.instances = instances
        self.app_config1 = app_config1
        self.app_config2 = app_config2

    def get_token(self):
        token_url = 'https://platform.ironsrc.com/partners/publisher/auth'
        headers = {
            'secretkey': self.secret,
            'refreshToken': self.refresh
        }

        return requests.get(url=token_url,
                            headers=headers).text.replace('"', '')

    @staticmethod
    def get_ad_type(instance) -> str:
        match instance:
            case 'banner':
                return AdFormats1C.banner.name

            case 'interstitial':
                return AdFormats1C.inter.name

            case 'rewardedVideo':
                return AdFormats1C.reward.name

    @staticmethod
    def get_1c_letter(unit_name):
        match unit_name:
            case 'banner':
                return 'b.bid.'
            case 'interstitial':
                return 'i.bid.'
            case 'rewardedVideo':
                return 'v.bid.'

    def get_instances(self, app_key):
        url = f'https://platform.ironsrc.com/partners/publisher/instances/v3?appKey={app_key}'

        return requests.get(url=url,
                            headers=self.headers)

    @staticmethod
    def convert_ad_type(ad_format: IronSourceAdFormats) -> str:
        match ad_format:
            case IronSourceAdFormats.INTER:
                return 'inter'
            case IronSourceAdFormats.BANNER:
                return 'banner'
            case IronSourceAdFormats.REWARD:
                return 'reward'
            case _:
                raise WrongPlacementTypeException

    @staticmethod
    def convert_banner_name_to_type(name: str) -> str:
        match name[0]:
            case 'b':
                return 'banner'
            case 'i':
                return 'inter'
            case 'r':
                return 'reward'
            case _:
                raise WrongPlacementTypeException

    def get_apps(self):
        url = f'https://platform.ironsrc.com/partners/publisher/applications/v4?'

        return requests.get(url=url,
                            headers=self.headers)

    def get_groups_ids(self, app_id, ad_type=None):
        url = f'https://platform.ironsrc.com/partners/publisher/mediation/management/v2?appKey={app_id}'

        req = requests.get(url=url,
                           headers=self.headers).json()

        if ad_type:
            return {i: req['adUnits'][i][0].get("groupId") for i in req.get('adUnits')}[ad_type]
        else:
            return {i: req['adUnits'][i][0].get("groupId") for i in req.get('adUnits')}

    def activate_instances(self, app_id):

        """
        requests.put(url=url, headers=headers, json={   "appKey": "17a56c225","configurations": {"ironSourceBidding":
        {"rewardedVideo": [{"instanceId": 11491765,"status": "active"}]}}})
        """

        url_instances = f'https://platform.ironsrc.com/levelPlay/network/instances/v4/{app_id}'

        req = requests.get(url=url_instances,
                           headers=self.headers)

        ad_units = {i.get('adUnit'): i.get('instanceId') for i in req.json()}


        groups = self.get_groups_ids(app_id=app_id)

        data = []

        if IronSourceAdFormats.INTER in self.ad_format:
            data.append({
                "instanceId": ad_units.get('interstitial'),
                "isLive": True,
                "groups": [groups.get('interstitial')]
            })
        else:
            ad_units.pop('interstitial')

        if IronSourceAdFormats.BANNER in self.ad_format:
            data.append({
                "instanceId": ad_units.get('banner'),
                "isLive": True,
                "groups": [groups.get('banner')]
            })
        else:
            ad_units.pop('banner')

        if IronSourceAdFormats.REWARD in self.ad_format:
            data.append({
                "instanceId": ad_units.get('rewardedVideo'),
                "isLive": True,
                "groups": [groups.get('rewardedVideo')]
            })
        else:
            ad_units.pop('rewardedVideo')

        req = requests.put(
            url=url_instances,
            headers=self.headers,
            json=data
        )

        if req.status_code == 200:
            return ad_units
        else:
            raise ProblemsWithPlacementActivation

    def create_app(self):
        url = 'https://platform.ironsrc.com/partners/publisher/applications/v6?'

        data = {
            'storeUrl': self.link,
            'taxonomy': self.taxonomy,
            # 'appName': self.bundle + 'delete_me45',
            'appName': self.bundle[:74],
            'coppa': 1 if self.kids else 0,
            'adUnits:status': {
                'RewardedVideo': 'Live' if IronSourceAdFormats.REWARD in self.ad_format else 'Off',
                'Interstitial': 'Live' if IronSourceAdFormats.INTER in self.ad_format else 'Off',
                'Banner': 'Live' if IronSourceAdFormats.BANNER in self.ad_format else 'Off',
                'OfferWall': 'Off'
            }
        }

        req = requests.post(url=url,
                            headers=self.headers,
                            json=data)

        if req.status_code == 200:
            app_id = json.loads(req.text).get('appKey')
            answer = {'app_id': app_id,
                      'instances': {}}
            answer['instances'].update(self.activate_instances(app_id=app_id))

            mediation_info = {}
            for banner_name in answer.get('instances'):
                mediation_info[self.convert_banner_name_to_type(banner_name)] = {
                    'myBundle': self.bundle,
                    'mediationBundle': self.bundle,
                    'AppId': app_id,
                    'PlacementId': answer.get('instances').get(banner_name),
                    'mediationName': 'IS'
                }

            self.db.send_mediation_info(
                mediation_info
            )

            info_to_send = []

            for unit in answer.get('instances'):
                info_to_send.append(
                    json.dumps({
                        'name': ('a.' if self.is_android else 'i.') + self.get_1c_letter(
                            unit) + self.bundle + f' IronSource{"" if self.kids else " Adult"}',
                        'mark': 'Bid',
                        'PlacementID': unit,
                        'app': self.bundle,
                        'bannerType': self.get_ad_type(unit),
                        'platform': self.get_platform(self.is_android),
                        'account': f'IronSource{"" if self.kids else " Adult"}',
                        'rtb': answer.get('instances')[unit],
                        'appId': answer.get('app_id'),
                        'mediation': MediationTo1cConvertor.convert(self.mediation)
                    })
                )

            for info in info_to_send:
                self.db.send_to_1c(
                    ad_service=f'IronSource{"" if self.kids else " Adult"}',
                    json=info,
                    username=self._user_name
                )

            return True

        elif 'Cannot have 2 applications with the same naming' in json.loads(req.text).get('message'):
            raise AlreadyCreatedApp

        elif 'Taxonomy' in json.loads(req.text).get('message'):
            raise WrongTaxonomy

        elif 'No data available for the required URL' in json.loads(req.text).get('message'):
            raise CannotFindApp

        else:
            raise CannotCreateApp

    def full_fill_placement(self, app_id,
                            provider_name, ad_format,
                            app_config1, app_config2,
                            instance_config1, instance_config2):
        data = {
            "networkName": provider_name,
            "adUnit": ad_format,
            "isBidder": True,
            "instanceConfig1": instance_config1,
            "instanceConfig2": instance_config2,
            "groups": [self.get_groups_ids(app_id=app_id, ad_type=ad_format)],
            "isLive": True,
            "rate": 2
        }

        try:
            if self.app_config2:
                data.update({"appConfig2": app_config2})
        except AttributeError:
            pass

        try:
            if self.app_config1:
                data.update({"appConfig1": app_config1})
        except AttributeError:
            pass

        req = requests.post(
            url=f'https://platform.ironsrc.com/levelPlay/network/instances/v4/{app_id}',
            headers=self.headers,
            json=[data])

        if req.status_code == 200:
            return True

        raise CannotAdMediation

    def add_mediation(self):
        info = self.db.get_mediation_info(mediation=self.mediation,
                                          bundle=self.bundle,
                                          banner_type=self.convert_ad_type(self.ad_format[0]))
        if info:
            for instance in self.instances:
                self.full_fill_placement(provider_name=self.provider_name,
                                         app_config1=self.app_config1,
                                         app_config2=self.app_config2,
                                         instance_config1=self.instances.get(instance),
                                         instance_config2=self.instances.get(instance),
                                         app_id=info.get('AppId'),
                                         ad_format=BaseToISConvertor.ad_format(instance)
                                         )

        else:
            raise NotAddedInIronSource


# print(IronSource(bundle='net.gameo.roadlimits',
#                  is_android=True,
#                  kids=False,
#                  taxonomy='Other Mid-Core',
#                  ad_format=[IronSourceAdFormats.INTER, IronSourceAdFormats.REWARD,
#                             IronSourceAdFormats.BANNER]).create_app())

# print(IronSource(bundle='com.occess.hero.fighter.battle.royale.spiderhero.games.shooting.commando.arena',
#                  is_android=True,
#                  kids=False,
#                  taxonomy='Other Mid-Core',
#                  ad_format=[IronSourceAdFormats.INTER, IronSourceAdFormats.REWARD,
#                             IronSourceAdFormats.BANNER]).full_fill_placement(
#     app_id='1b8fb9825',
#     ad_format=BaseToISConvertor.ad_format('banner'),
#     app_config1='AdColony_app_Config',
#     app_config2=None,
#     provider_name='adColony',
#     instance_config1='AdColony_instance_Config',
#     instance_config2='AdColony_instance_Config'
# ))

# self.instance_config = {'placementId': instance_config}
#         #         self.app_config = {}
