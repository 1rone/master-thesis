import json
import time
import requests
from AdServices.AdService import AdService
from DataBase.MySql import MySql
from AdServices.PlacementsId.YandexPlacementsId import YandexPlacements
from Exceptions.Exceptions import *
from Config.config import DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_PORT
from Enums.Enums import AdFormats
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor


def price_normal(price):
    if 'def' in price.lower() or 'bid' in price.lower():
        return 0
    else:
        price = price[2:-1]
        if price[0] == '0':
            price = price[1:]
        while price[-1] == '0' or price[-1] == '.':
            price = price[:-1]
        return price


class Yandex(AdService):
    def __init__(self, bundle, is_android, ad_format, mediation):
        super().__init__()
        self.bundle = bundle
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.is_android = is_android
        self.ad_format = ad_format
        self.mediation = mediation
        self.cookie = self.get_header(MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT).get_headers(
            ad_service='Yandex',
            header_name='Cookie'))
        self.token = self.get_token()

    def get_token(self):
        url = 'https://partner.yandex.ru/restapi/v1/resources'

        headers = {
            'Accept': 'application/vnd.api+json',
        }

        headers.update(self.cookie)

        req = requests.get(url=url,
                           headers=headers)

        match req.status_code:
            case 200:
                answer = {'X-Frontend-Authorization': req.headers['X-Frontend-Authorization']}
            case _:
                raise CannotGetToken

        return answer

    def get_headers(self):
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'partner.yandex.ru',
            'Origin': 'https://partner.yandex.ru',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            'Referer': 'https://partner.yandex.ru/v2/inapp/app/create',
            'Connection': 'keep-alive',
            'x-skeleton-disabled': 'true'
        }

        headers.update({**self.cookie, **self.token})
        return headers

    def get_bundle_and_link(self):
        url = f'https://partner.yandex.ru/restapi/v1/api/uac/app_info/search_or_' \
              f'add?text={self.link}&limit=10'

        headers = self.get_headers()

        req = requests.post(url=url, headers=headers)

        if req.status_code == 401:
            self.token = self.get_token()
            headers = self.get_headers()
            req = requests.post(url=url,
                                headers=headers)
            if req.status_code == 401:
                raise WrongToken

        try:
            req = json.loads(req.text).get('data')[0]
        except IndexError:
            raise CannotFindApp
        except TypeError:
            raise CannotFindApp

        self.link = req.get('url')

        return req.get('bundle')

    def create_app(self):
        url = 'https://partner.yandex.ru/restapi/v1/mobile_app'

        headers = self.get_headers()

        body = {"data": {"attributes": {"store_id": f"{self.get_bundle_and_link()}",
                                        "store_url": f"{self.link}",
                                        "type": 1 if self.is_android else 2}, "type": "mobile_app"}}

        local_id = json.loads(requests.post(url=url,
                                            headers=headers,
                                            data=json.dumps(body)).text).get('data').get('id')

        url = 'https://partner.yandex.ru/restapi/v1/mobile_app_settings'

        body = {"data": {"attributes": {"app_id": f"{local_id}", "caption": f"{self.bundle}"},
                         "type": "mobile_app_settings"}}

        req = requests.post(url=url,
                            headers=headers,
                            data=json.dumps(body))

        if req.status_code == 401:
            self.token = self.get_token()
            headers = self.get_headers()
            req = requests.post(url=url,
                                headers=headers,
                                data=json.dumps(body))
            if req.status_code == 401:
                raise WrongToken

        app_id = json.loads(req.text).get('data').get('id')

        print(f'Створив додаток під назвою: {self.bundle}')

        return app_id

    def create_placement(self, app_id, ad_format, price, name):

        def get_body(strategy, page_id=app_id):
            data = {"data": {"attributes": {"adfox_block": False,
                                            'caption': name,
                                            "geo": "[]", "page_id": f"{page_id}", "strategy": f"{strategy}"},
                             "type": "mobile_app_rtb"}}
            if not strategy:
                data['data']['attributes']['mincpm'] = f'{price}'

            match ad_format:
                case AdFormats.banner:
                    data['data']['attributes']['block_type'] = 'banner'
                    data['data']['attributes']['show_video'] = 1
                case AdFormats.inter:
                    data['data']['attributes']['block_type'] = 'interstitial'
                    data['data']['attributes']['close_button_delay'] = None
                case AdFormats.reward:
                    data['data']['attributes']['block_type'] = 'rewarded'
                    data['data']['attributes']['currency_type'] = 'Rewarded'
                    data['data']['attributes']['currency_value'] = 1
                case _:
                    raise WrongPlacementTypeException

            return data

        url = 'https://partner.yandex.ru/restapi/v1/mobile_app_rtb'

        headers = self.get_headers()

        body = json.dumps(get_body(0 if price else 1))

        req = requests.post(url=url,
                            headers=headers,
                            data=body)

        if req.status_code == 401:
            self.token = self.get_token()
            headers = self.get_headers()
            req = requests.post(url=url,
                                headers=headers,
                                data=body)
            if req.status_code == 401:
                raise WrongToken

        placement = json.loads(req.text).get('data').get('id')
        return placement

    def get_activate_id(self, app_id):
        url = f'https://partner.yandex.ru/restapi/v1/mobile_app_settings/{app_id}?' \
              'fields%5Bmobile_app_settings%5D=actions%2Capp_is_approved%2Capplication_id' \
              '%2Cassistants%2Cavailable_blocks%2Cavailable_fields%2Cbk_languages%2Cblocks_count' \
              '%2Cblocks_limit%2Ccaption%2Ccomment%2Cclient_id%2Ccur_user_is_read_assistant%2Cdeveloper' \
              '%2Ceditable_fields%2Cexcluded_domains%2Cfast_context%2Cfilters%2Cglobal_excluded_domains%2' \
              'Chas_mediation_block%2Cicon%2Cignore_domain_check%2Cis_easy_monetization%2Cis_deleted%2Cis_protected' \
              '%2Cis_remoderation_available%2Cis_sdk_version_outdated%2Cis_updating%2Clatest_sdk_version%2C' \
              'max_used_sdk_version%2Cmoderation_reason_name%2Cmoneymap%2Csingle_state%2Conly_picture%2Corder_tags%2' \
              'Cowner_id%2Cpage_id%2Cpatch%2Cperformance_tgo_disable%2Cpicategories%2Cstore_url%2Cstore_id%2C' \
              'target_tags%2Cview_images%2Cwhen_remoderation_available%2Cplatform%2Cplatform_name&fields%5B' \
              'mobile_app_owner%5D=id%2Csingle_state%2Cverification_reason%2Cignore_verification&' \
              'include=mobile_app_owner'

        req = requests.get(url=url,
                           headers=self.get_headers())

        text = req.json().get('included')[0].get('id')

        return text

    def activate_app(self, activation_id):
        url = f'https://partner.yandex.ru/restapi/v1/mobile_app_owner/{activation_id}/action/ads_ownership_verification'

        req = requests.post(url=url,
                            headers=self.get_headers())

        return True

    def auto_writing(self):
        try:
            app_id = self.create_app()
        except WrongToken:
            raise WrongToken
        except CannotFindApp:
            raise CannotFindApp
        except Exception as err:
            print(err)
            raise AlreadyCreatedApp
        try:
            yandex_placements = YandexPlacements()
        except Exception:
            raise ProblemsWithPlacementCreation
        placements_ids_names = {}
        for ad_format in self.ad_format:
            match ad_format:
                case AdFormats.banner:
                    placements = yandex_placements.get_banner()
                    for placement in placements:
                        placements_ids_names[self.create_placement(app_id=app_id,
                                                                   ad_format=ad_format,
                                                                   price=price_normal(placements[placement]),
                                                                   name=placement)] = placements[placement]
                        print(f'Створив banner під назвою {placement}')
                        time.sleep(2)

                case AdFormats.reward:
                    placements = yandex_placements.get_rewarded()
                    for placement in placements:
                        placements_ids_names[self.create_placement(app_id=app_id,
                                                                   ad_format=ad_format,
                                                                   price=price_normal(placements[placement]),
                                                                   name=placement)] = placements[placement]
                        print(f'Створив rewarded під назвою {placement}')
                        time.sleep(2)

                case AdFormats.inter:
                    placements = yandex_placements.get_interstitial()
                    for placement in placements:
                        placements_ids_names[self.create_placement(app_id=app_id,
                                                                   ad_format=ad_format,
                                                                   price=price_normal(placements[placement]),
                                                                   name=placement)] = placements[placement]
                        print(f'Створив interstitial під назвою {placement}')
                        time.sleep(2)

        info_to_send = []

        self.activate_app(activation_id=self.get_activate_id(app_id=app_id))

        for unit in placements_ids_names:
            info_to_send.append(
                json.dumps({
                    'name': ('a.' if self.is_android else 'i.') + f'{placements_ids_names[unit]}{self.bundle} Yandex',
                    'app': self.bundle,
                    'mark': self.get_mark(placements_ids_names[unit], is_bid=False),
                    'bannerType': self.get_ad_type('x.' + placements_ids_names[unit]),
                    'platform': self.get_platform(self.is_android),
                    'account': 'Yandex',
                    'id': unit,
                    'mediation': MediationTo1cConvertor.convert(self.mediation) if self.get_mark(
                        placements_ids_names[unit]) == 'Def' else ''
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
                ad_service='Yandex',
                json=info,
                username=self._user_name
            )

        return True

# Yandex(bundle='net.gameo.roadlimits',
#        is_android=True,
#        ad_format=[AdFormats.inter, AdFormats.banner, AdFormats.reward],
#        mediation=Mediators.CAS.value).auto_writing()
