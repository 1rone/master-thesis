import json
import requests
from AdServices.AdService import AdService
from AdServices.Mediators.MaxMediation import MaxMediation
from AdServices.Mediators.IronSourceMediation import IronSource
from Convertors.InputToInmobiConvertor import InputToInmobiConvertor
from Exceptions.Exceptions import *
from DataBase.MySql import MySql
from Config.config import *
from Enums.Enums import AdFormats, MaxAdNetworks, Mediators, IronSourceAdNetworks as IS
from Convertors.InmobiToMaxConvertor import InmobiToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Convertors.InmobiToIronSourceConvertor import InmobiToIronSourceConvertor


def get_headers(rows) -> dict:
    headers = {}
    for row in rows:
        headers.update(
            {row.get('HeaderName'): row.get('HeaderValue')}
        )
    return headers


class Inmobi(AdService):

    def __init__(self, bundle, is_android, ad_format, kids, mediation, categories_id, consent_of_age):
        super().__init__()
        self.categories_id = categories_id
        self.consent_of_age = consent_of_age
        self.bundle = bundle
        self.is_android = is_android
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.api_url = 'https://publisher.inmobi.com/api/graphql'
        self.ad_format = ad_format
        self.mediation = mediation
        self.kids = kids
        self.message = 'Успішно. '
        self.cookies = get_headers(MySql(host=DB_SENDER_HOST,
                                         user=DB_SENDER_USER,
                                         password=DB_SENDER_PASSWORD,
                                         db=DB_SENDER_NAME,
                                         port=DB_SENDER_PORT).get_headers(
            ad_service='Inmobi kids' if self.kids else 'Inmobi adults',
            header_name='Cookie'))
        self.xtk = get_headers(MySql(host=DB_SENDER_HOST,
                                     user=DB_SENDER_USER,
                                     password=DB_SENDER_PASSWORD,
                                     db=DB_SENDER_NAME,
                                     port=DB_SENDER_PORT).get_headers(
            ad_service='Inmobi kids' if self.kids else 'Inmobi adults',
            header_name='x-tk'))

        self.code = 0

    def get_app_info(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        headers.update({**self.cookies, **self.xtk})

        data = json.dumps({"query": "query appMeta($payload:AppMetaPayload){appMeta(payload:$payload)"
                                    "{name iconUrl bundleId marketId creator platform{id name}categories"
                                    "{id name iabStandardId}contentRating{id rating}}}",
                           "variables": "{\"payload\":"
                                        "{\"appUrl\":\""
                                        f"{self.link}"
                                        "\"}}"})

        req = requests.get(url=self.api_url, headers=headers, data=data)

        match req.status_code:
            case 403 | 401:
                raise WrongToken
            case 200:
                req = json.loads(req.text)

                if req.get('errors'):
                    if 'app metadata not found' in req.get('errors')[0].get('message').lower():
                        raise CannotFindApp
                    else:
                        raise Exception

                try:

                    answer = {
                        'id': req.get('data'),
                        'icon': req.get('data').get('appMeta').get('iconUrl'),
                        'bundle': req.get('data').get('appMeta').get('bundleId'),
                        'marketId': req.get('data').get('appMeta').get('marketId'),
                        'platformId': req.get('data').get('appMeta').get('platform').get('id'),
                        'contentRatingId': req.get('data').get('appMeta').get('contentRating').get('id')
                    }

                    if req.get('data').get('appMeta').get('categories'):
                        answer.update({'categoriesIds': [int(i['id']) for i in
                                                         req.get('data').get('appMeta').get('categories')]})
                    else:
                        answer.update({'categoriesIds': [5, 196]})
                        self.code = 1

                    answer.update(
                        {'categoriesIds': [int(i['id']) for i in
                                           req.get('data').get('appMeta').get('categories')] if req.get('data').get(
                            'appMeta').get('categories') else [5, 196]}
                    )

                    return answer
                except AttributeError:
                    if req.get('data').get('appMeta').get('categories'):
                        raise CannotGetAppId
                    else:
                        raise CannotGetCategories
            case _:
                raise CannotGetAppId

    def get_all_mediators(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'publisher.inmobi.com',
            'Origin': 'https://publisher.inmobi.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            'Referer': f'https://publisher.inmobi.com/my-inventory/app-and-placements/create-placement/1498907686685',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        headers.update({**self.cookies, **self.xtk})

        data = json.dumps({
            "query": "query getAudienceBiddingChannelList($payload:String!)"
                     "{getAudienceBiddingChannelList(payload:$payload){id name displayName}}",
            "variables": "{\"payload\":\"1489138483904054\"}"})

        req = json.loads(requests.post(url=self.api_url,
                                       headers=headers,
                                       data=data).text).get('data')['getAudienceBiddingChannelList']

        return {i['name']: i['id'] for i in req}

    def create_app(self):
        info = self.get_app_info()
        data = {"query": "mutation createApp($payload:createAppPayload){createApp(payload:$payload)"
                         "{id name supplyChannels platform{id name}bundleId url iconUrl compliance"
                         "{consentOfAge enableLocation}categories{id name iabStandardId}"
                         "contentRating{id rating}status blockAssociationSuccessful sensitiveAdCategories}}",
                "variables": "{\"payload\":"
                             "{\"name\":\""
                             f"{self.bundle}"
                             "\",\"supplyChannels\":[\"IN_APP\"],"
                             "\"platformId\":"
                             f"{info['platformId']}"
                             ",\"url\":\""
                             f"{self.link}"
                             "\",\"iconUrl\":\""
                             f"{info['icon']}"
                             "\",\"marketId\":\""
                             f"{info['marketId']}"
                             "\",\""
                             "categoryIds\":"
                             f"{info['categoriesIds']}"
                             ",\"autoCategorized\":false,\"contentRatingId\":"
                             f"{info['contentRatingId']}"
                             ",\"uacAutoPopulated\":"
                             "{\"bundleId\":true,"
                             "\"categories\":true,"
                             "\"contentRating\":true},"
                             "\"sensitiveAdCategories\":[],\"compliance\":"
                             "{\"consentOfAge\":"
                             f'{self.consent_of_age}'
                             ",\"enableLocation\":"
                             "false""}"
                             ",\"blockSettingsId\":673"
                             "}}"}

        if self.categories_id == 0:
            data['variables'] = data['variables'].replace(',\"blockSettingsId\":673', '')
        else:
            data['variables'] = data['variables'].replace(',\"blockSettingsId\":673', f',\"blockSettingsId\":'
                                                                                      f'{self.categories_id}')

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        headers.update({**self.cookies, **self.xtk})

        req = requests.post(url=self.api_url,
                            headers=headers,
                            data=json.dumps(data))
        match req.status_code:
            case 403 | 401:
                raise WrongToken
            case 200:
                try:
                    return json.loads(req.text).get('data').get('createApp').get('id')
                except AttributeError:
                    if 'DUPLICATE_APP' in req.text:
                        raise AlreadyCreatedApp
                    else:
                        raise CannotCreateApp
            case _:
                raise CannotCreateApp

    def create_placement(self, ad_format, app_id):

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'publisher.inmobi.com',
            'Origin': 'https://publisher.inmobi.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            'Referer': f'https://publisher.inmobi.com/my-inventory/app-and-placements/create-placement/{app_id}',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        headers.update({**self.cookies, **self.xtk})

        if self.is_android:
            name = 'a.'
        else:
            name = 'i.'

        if ad_format == AdFormats.banner:
            ad_format_id = 3
            name += 'b.bid'
        elif ad_format == AdFormats.inter:
            ad_format_id = 1
            name += 'i.bid'
        elif ad_format == AdFormats.reward:
            ad_format_id = 6
            name += 'v.bid'
        else:
            raise WrongPlacementTypeException

        data = json.dumps({
            "query": "mutation createPlacement($payload:createPlacementPayload!)"
                     "{createPlacement(payload:$payload){id appId adUnitTypeId name testMode audienceBiddingChannelInfo"
                     "{enabled id audienceBiddingChannelSpecificInfo{abPartnerIdKey abPartnerIdValue}}uxTemplate"
                     "{id name isSystemTemplate adUnitTypeId appMetaData{id iconUrl name supplyChannels}}"
                     "restrictedPmpSupply deviceIdForwardingRestricted}}",
            "variables": "{\"payload\":"
                         "{\"appId\":"
                         f"{app_id},"
                         "\"adUnitTypeId\":"
                         f"{ad_format_id},"
                         "\"name\":\""
                         f"{name}"
                         "\","
                         "\"audienceBiddingChannelInfo\":"
                         "{\"id\":"
                         f"{InputToInmobiConvertor.mediation_id(self.mediation)},"
                         "\"enabled\":true},"
                         "\"testMode\":3,"
                         "\"supplyChannelType\":\"IN_APP\"}}"})

        req = requests.post(url=self.api_url,
                            headers=headers,
                            data=data)
        match req.status_code:
            case 403 | 401:
                raise WrongToken
            case 200:
                try:
                    return [name, json.loads(req.text).get('data').get('createPlacement').get('id')]
                except AttributeError:
                    raise ProblemsWithPlacementCreation
            case _:
                raise ProblemsWithPlacementCreation

    def auto_writing(self):
        app_id = self.create_app()
        placements = []
        for ad_format in self.ad_format:
            placements.append(self.create_placement(ad_format=ad_format,
                                                    app_id=app_id))

        info_to_send = []

        is_info = {}

        for unit in placements:
            info_to_send.append(
                json.dumps({
                    'name': unit[0] + f'.{self.bundle} ' + ('InMobi kids' if self.kids else 'InMobi adult'),
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit[0]),
                    'platform': self.get_platform(self.is_android),
                    'account': 'InMobi kids' if self.kids else 'InMobi adult',
                    'rtb': unit[1],
                    'mark': self.get_mark(unit[0], is_bid=True),
                    'mediation': MediationTo1cConvertor.convert(mediation=self.mediation)
                })
            )

            if unit[0][2] == 'i':
                is_info['inter'] = str(unit[1])

            if unit[0][2] == 'b':
                is_info['banner'] = str(unit[1])

            if unit[0][2] == 'v':
                is_info['reward'] = str(unit[1])

            if InputToInmobiConvertor.mediation_id(self.mediation) == 2:
                # ЦЕ ПРАЦЮЄ ТІЛЬКИ ПОКИ В НАС mark = 'Def'!!!!!!
                try:
                    message = MaxMediation(
                        ad_format=InmobiToMaxConvertor.convert_ad_format(unit[0]),
                        platform=InmobiToMaxConvertor.convert_platform(is_android=self.is_android),
                        bundle=self.bundle,
                        kids=self.kids,
                        ad_network=MaxAdNetworks.Inmobi,
                        unit_id=unit[1],
                        app_key=None,
                        app_id=app_id
                    ).add_mediation()
                    if message and len(info_to_send) == 1:
                        self.message += message
                    self.message += f'Додав у MAX {self.get_ad_type(unit[0])}. '
                except Exception:
                    self.message += f'Не зміг додати в MAX {self.get_ad_type(unit[0])}. '

        if InputToInmobiConvertor.mediation_id(self.mediation) == 6:
            try:
                message = IronSource(
                    ad_format=InmobiToIronSourceConvertor.convert_ad_formats(self.ad_format),
                    is_android=self.is_android,
                    bundle=self.bundle,
                    kids=self.kids,
                    taxonomy=None,
                    provider_name=IS.Inmobi.value,
                    app_config1=None,
                    app_config2=None,
                    instances=is_info
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти. '
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
                ad_service='InMobi kids' if self.kids else 'InMobi adult',
                json=info,
                username=self._user_name
            )

        match self.code:
            case 1:
                self.message += 'Потрібно вручну проставити категорії в InMobi!'
            case _:
                self.message += ''

        return True, self.message


# print(Inmobi(ad_format=[AdFormats.banner, AdFormats.inter, AdFormats.reward],
#              bundle='com.movies.sfera',
#              is_android=True,
#              kids=False,
#              categories_id=0,
#              mediation=Mediators.IS.value,
#              consent_of_age=1).auto_writing())
