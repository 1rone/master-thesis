import json
import time
import requests

from AdServices.Mediators.IronSourceMediation import IronSource
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor
from Convertors.UnityToIronSourceConveror import UnityToIronSourceConvertor
from DataBase.MySql import MySql
from AdServices.PlacementsId.UnityPlacementsId import KidsPlacements, AdultsPlacements
from Config.config import UNITY_ADULTS_ORG_ID, UNITY_KIDS_ORG_ID, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import WrongToken, AlreadyCreatedApp, WrongStatusCode, WrongMediationName, \
    WrongPlacementNameException
from AdServices.AdService import AdService
from Enums.Enums import AdFormats, Mediators
from Enums.Enums import IronSourceAdNetworks as IS


def get_category_dict(blocked_categories: list,
                      is_android: bool) -> dict:
    all_categories = {
        "blacklistCategories": {"dice": False, "action": False, "adventure": False, "arcade": False, "word": False,
                                "card": False, "casino": False, "educational": False, "family": False, "board": False,
                                "fighting": False, "music": False, "parkour": False, "planeShooting": False,
                                "puzzle": False, "racing": False, "role playing": False, "simulation": False,
                                "sports": False, "strategy": False, "towerDefence": False, "trivia": False},
        "blacklistCategoryGroups": {"healthMedicine": False, "healthFitnessApps": False, "food": False,
                                    "alcoholicBeverages": False, "lotteryGambling": False,
                                    "lawGovernmentPolitics": False, "newsWeather": False, "personalFinance": False,
                                    "datingSocialMedia": False, "contestsShopping": False,
                                    "religionSpirituality": False},
        "blacklistSensitiveAttributes": {"realMoneyGambling": True}}

    answer = {
        "blacklistCategories": {
            "add": [],
            "remove": []
        },
        "blacklistCategoryGroups": {
            "add": [],
            "remove": []
        },
        "blacklistSensitiveAttributes": {
            "add": [],
            "remove": []
        }
    }

    classic_dict = {
        "id": '',
        "store": 'google' if is_android else 'apple'
    }

    for cat_name in all_categories:
        for category in all_categories[cat_name]:
            if category in blocked_categories:
                classic_dict['id'] = category
                answer[cat_name]['add'].append(classic_dict.copy())
                # all_categories[cat_name][category] = (True if category in blocked_categories else False)

    return answer


class Unity(AdService):

    def __init__(self, is_android: bool, bundle: str, ad_format: [str], categories: [str], age: str, kids: bool,
                 mediation: str):
        super().__init__()
        self.org_id = UNITY_KIDS_ORG_ID if kids else UNITY_ADULTS_ORG_ID
        self.name = bundle
        self.is_android = is_android
        self.headers = self.get_header(MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT).get_headers(
            ad_service='Unity kids' if kids else 'Unity adults',
            header_name='Authorization'))
        self.bundle = bundle
        self.kids = kids
        self.mediation = mediation
        self.message = 'Успішно. '
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        # self.link = 'https://play.google.com/store/apps/details?id=net.gameo.roadlimits' if
        # is_android else 'https://apps.apple.com/us/app/rec-room/id1609982306'
        self.ad_format = ad_format
        self.categories = categories
        self.age = age

    def get_all_ad_units(self, mediation):
        if mediation == Mediators.CAS.value:
            if self.kids:
                if len(self.ad_format) == 3:
                    return KidsPlacements().get_banner_and_interstitial_and_rewarded()
                elif AdFormats.banner in self.ad_format:
                    return KidsPlacements().get_banner_and_interstitial()
                else:
                    return KidsPlacements().get_interstitial_and_rewarded()
            else:
                if len(self.ad_format) == 3:
                    return AdultsPlacements().get_banner_and_interstitial_and_rewarded()
                elif AdFormats.banner in self.ad_format:
                    return AdultsPlacements().get_banner_and_interstitial()
                else:
                    return AdultsPlacements().get_interstitial_and_rewarded()

        elif mediation == Mediators.IS.value:
            answer = {}
            if AdFormats.banner in self.ad_format:
                answer.update({'banner': 'b_bid'})

            if AdFormats.inter in self.ad_format:
                answer.update({'inter': 'i_bid'})

            if AdFormats.reward in self.ad_format:
                answer.update({'reward': 'v_bid'})

            if answer:
                return answer
            else:
                raise WrongPlacementNameException

        else:
            raise WrongMediationName

    def get_app_to_copy_id(self, mediation):
        copy_name = 'AUTO_'
        if self.is_android:
            copy_name += 'A_'
        else:
            copy_name += 'I_'
        if mediation == Mediators.CAS.value:
            if len(self.ad_format) == 3:
                copy_name += 'B_I_V'
            elif AdFormats.banner in self.ad_format:
                copy_name += 'B_I_0'
            else:
                copy_name += '0_I_V'
            if self.kids:
                if copy_name == 'AUTO_A_0_I_V':
                    return 'c214c14d-c5bc-4ac3-9913-7e041bc532f3'
                elif copy_name == 'AUTO_A_B_I_0':
                    return 'dcbb023b-b545-49ae-b713-62c451f333d4'
                elif copy_name == 'AUTO_A_B_I_V':
                    return '36d2ca75-edb4-4dc6-910d-5f314177916b'
                elif copy_name == 'AUTO_I_0_I_V':
                    return 'e491b0a9-0652-48a2-a8b7-f2decf579434'
                elif copy_name == 'AUTO_I_B_I_0':
                    return 'bd52049b-ee61-4e09-8b3f-1a020875abfc'
                else:
                    return '1e1b158d-74f5-409b-ad51-b6e88279aa49'
            else:
                if copy_name == 'AUTO_A_0_I_V':
                    return '9b98fe54-3ad1-40dc-ae25-722228c851fc'
                elif copy_name == 'AUTO_A_B_I_0':
                    return 'd56792ec-e61f-43a9-871d-6d8ff62e9302'
                elif copy_name == 'AUTO_A_B_I_V':
                    return 'f0d8f445-4eef-4a95-9489-3c30d6465300'
                elif copy_name == 'AUTO_I_0_I_V':
                    return 'cf07341e-7143-4997-ac66-8aad64e84d1d'
                elif copy_name == 'AUTO_I_B_I_0':
                    return '4e39e53f-c08c-459b-87bc-4c565435ad4d'
                else:
                    return 'db917c22-77a8-4991-bb71-784cb0eefe71'
        elif mediation == Mediators.IS.value:
            if AdFormats.banner in self.ad_format:
                copy_name += 'B_'
            if AdFormats.inter in self.ad_format:
                copy_name += 'I_'
            if AdFormats.reward in self.ad_format:
                copy_name += 'V_'
            copy_name += 'BIDDING'

            if self.kids:
                match copy_name:
                    case 'AUTO_A_B_BIDDING':
                        return '4ed46b86-32f0-4992-a1c7-5f103d78013d'
                    case 'AUTO_A_B_I_BIDDING':
                        return '05019fb6-8a8d-4c15-9c30-4dc3688acedd'
                    case 'AUTO_A_B_V_BIDDING':
                        return '25ecaf4c-aab6-48b4-8abb-708f651deddb'
                    case 'AUTO_A_B_I_V_BIDDING':
                        return '221a9cec-c31e-4835-92f6-e8304ee99dbd'
                    case 'AUTO_A_I_V_BIDDING':
                        return 'b1ce6e62-0042-4d43-bb82-8b10bdfc6fb8'
                    case 'AUTO_A_I_BIDDING':
                        return 'c7666bcd-4876-4804-b102-58d5b3c97476'
                    case 'AUTO_A_V_BIDDING':
                        return 'b0c02bd4-e1fc-4434-8c88-f062bcd18bd3'

                    case 'AUTO_I_B_BIDDING':
                        return 'fca95f7a-d1b3-47a3-b0b8-ea1d3af43b1d'
                    case 'AUTO_I_B_I_BIDDING':
                        return '13fdcffd-b243-41e5-9406-cc998bacb109'
                    case 'AUTO_I_B_V_BIDDING':
                        return '3e2e01e7-adf6-4e87-9027-c37cf6dc3e07'
                    case 'AUTO_I_B_I_V_BIDDING':
                        return 'be22db31-0e53-4fe7-8ee5-03c5bf35533d'
                    case 'AUTO_I_I_V_BIDDING':
                        return '4e546481-e9e0-4ed6-90a6-08c7cd10a575'
                    case 'AUTO_I_I_BIDDING':
                        return '636ee0a1-76a8-4f36-a3b3-c0a0abc034dc'
                    case 'AUTO_I_V_BIDDING':
                        return '77a21472-670a-4844-88bc-5f52bdf69595'
                    case _:
                        raise WrongPlacementNameException
            else:
                match copy_name:

                    case 'AUTO_A_B_BIDDING':
                        return 'eba029a9-b2dc-478c-9cad-fea2eabd6711'
                    case 'AUTO_A_B_I_BIDDING':
                        return '460ddbc3-a45f-4e50-b9de-c1c9359c2e99'
                    case 'AUTO_A_B_V_BIDDING':
                        return '392fbd9f-1afe-44a6-ac0c-e6dc4e61ec3c'
                    case 'AUTO_A_B_I_V_BIDDING':
                        return '2168d163-5865-49a8-99bc-b5b92dd48c54'
                    case 'AUTO_A_I_V_BIDDING':
                        return 'e20433a1-f42b-407a-9d7d-7e76eec694a4'
                    case 'AUTO_A_I_BIDDING':
                        return '9bf4c10b-823a-48c6-a39c-0c12728f1972'
                    case 'AUTO_A_V_BIDDING':
                        return '0381fe6a-811f-4c07-bad6-e2d9d9961f15'

                    case 'AUTO_I_B_BIDDING':
                        return 'a27c0b63-7562-4f8f-8a44-f9b7e0a20520'
                    case 'AUTO_I_B_I_BIDDING':
                        return '049a6b78-c9b3-4e2e-ba3f-5fee8d09957d'
                    case 'AUTO_I_B_V_BIDDING':
                        return '121ec8d7-453a-49c4-9438-3e705542740b'
                    case 'AUTO_I_B_I_V_BIDDING':
                        return 'b02d34e0-f82f-4729-8b79-386fb469344f'
                    case 'AUTO_I_I_V_BIDDING':
                        return '6b630c45-4320-4ae0-8f80-9fc8c36cdf6d'
                    case 'AUTO_I_I_BIDDING':
                        return 'f7f2db86-2519-4448-9732-89d7aef2d670'
                    case 'AUTO_I_V_BIDDING':
                        return 'adf3eacc-6643-4850-9288-ef4d26fbad35'
                    case _:
                        raise WrongPlacementNameException

        else:
            raise WrongMediationName

    def create_app(self):
        url = f'https://services.unity.com/api/unity/legacy/v1/organizations/{self.org_id}/projects'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://dashboard.unity3d.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            'X-Client-ID': 'unity-dashboard',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

        headers.update(self.headers)

        data = {"name": self.name,
                "coppa": "compliant" if self.kids else "not_compliant"}

        req = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )

        match req.status_code:
            case 401:
                raise WrongToken
            case 422:
                raise AlreadyCreatedApp
            case 200 | 201:
                return json.loads(req.text).get('id')
            case _:
                raise WrongStatusCode(req, req.text)

    def create_placements_like(self, app_id, app_id_to_copy):
        url = f'https://services.unity.com/api/monetize/v1/organizations/' \
              f'{self.org_id}/projects/{app_id_to_copy}/duplicate'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://dashboard.unity3d.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36',
            'X-Client-ID': 'unity-dashboard',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        headers.update(self.headers)

        store_id = {"storeId": self.bundle}

        data = {
            "name": self.bundle,
            "coppa": True if self.kids else False,
            "coreId": app_id,
            "stores": {
                "apple": {},
                "google": {}
            }
        }

        data["stores"]["google"].update(store_id) if self.is_android else data["stores"]["apple"].update(store_id)

        req = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )

        match req.status_code:
            case 401:
                raise WrongToken
            case 200 | 201:
                return json.loads(req.text).get('stores').get('google' if self.is_android else 'apple').get('gameId')
            case _:
                raise WrongStatusCode(req, req.text)

    def add_age_settings_and_blocked_cat(self, app_id):

        url = f'https://services.unity.com/api/monetize/v1/projects/' \
              f'{app_id}/stores/{"google" if self.is_android else "apple"}'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://dashboard.unity3d.com',
            'Referer': 'https://dashboard.unity3d.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36',
            'X-Client-ID': 'unity-dashboard',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        headers.update(self.headers)

        data = {"maxAgeFilter": 0 if int(self.age) == 21 else int(self.age) - 1}

        if self.kids:
            data.update({"kidsSettings": True})

        req = requests.patch(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )

        match req.status_code:
            case 401:
                raise WrongToken
            case 200 | 201:
                pass
            case _:
                raise WrongStatusCode(req, req.text)

        if self.categories:
            data = get_category_dict(blocked_categories=self.categories,
                                     is_android=self.is_android)

            url = f'https://services.unity.com/api/monetize/v1/projects/' \
                  f'{app_id}/filters?publicIds=true'

            req = requests.patch(
                url=url,
                headers=headers,
                data=json.dumps(data)
            )

            match req.status_code:
                case 401:
                    raise WrongToken
                case 200 | 201:
                    pass
                case _:
                    raise WrongStatusCode(req, req.text)

    def activate_unity_play(self, app_id):

        headers = {
            'authority': 'services.unity.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://dashboard.unity3d.com',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'x-client-id': 'unity-dashboard'
        }

        headers.update(self.headers)

        requests.get(
            url=f'https://services.unity.com/api/monetize/au-switcher/v1/projects/{app_id}/validate-switch/iron_source',
            headers=headers
        )

        requests.patch(
            url=f'https://services.unity.com/api/monetize/au-switcher/v1/projects/{app_id}/au-switch',
            headers=headers,
            json={"adsProvider":"iron_source"}
        )


    def auto_writing(self):

        app_id = self.create_app()

        time.sleep(2)

        game_id = self.create_placements_like(app_id=app_id,
                                              app_id_to_copy=self.get_app_to_copy_id(mediation=self.mediation))

        time.sleep(2)

        self.add_age_settings_and_blocked_cat(app_id=app_id)

        info_to_send = []

        ad_format = self.get_all_ad_units(mediation=self.mediation)

        if self.mediation == Mediators.CAS.value:

            for unit_id in ad_format:
                info_to_send.append(
                    json.dumps({
                        'name': ('a.' if self.is_android else 'i.'
                                 ) + ad_format[unit_id] + self.bundle + f' Unity {"kids" if self.kids else "adults"}',
                        'PlacementID': unit_id,
                        'app': self.bundle,
                        'bannerType': self.get_ad_type('x.' + unit_id),
                        'platform': self.get_platform(self.is_android),
                        'account': f'Unity {"kids" if self.kids else "adults"}',
                        'GameID': str(game_id),
                        'mark': self.get_mark(ad_format[unit_id], is_bid=False),
                        'mediation': ''
                    })
                )

        elif self.mediation == Mediators.IS.value:

            self.activate_unity_play(app_id=app_id)

            is_info = ad_format
            try:
                message = IronSource(
                    ad_format=UnityToIronSourceConvertor.convert_ad_formats(placements=self.ad_format),
                    bundle=self.bundle,
                    kids=self.kids,
                    is_android=self.is_android,
                    taxonomy=None,
                    provider_name=IS.Unity.value,
                    app_config1=str(game_id),
                    app_config2=None,
                    instances=is_info
                ).add_mediation()
                if message and len(info_to_send) == 1:
                    self.message += message
                self.message += f'Додав у IronSource всі плейсменти.'
            except Exception:
                self.message += f'Не зміг додати в IronSource. '

            for unit_id in ad_format:
                info_to_send.append(
                    json.dumps({
                        'name': ('a.' if self.is_android else 'i.'
                                 ) + ad_format[unit_id].replace("_",
                                                                ".") + '.' + self.bundle + f' Unity {"kids" if self.kids else "adults"}',
                        'PlacementID': ad_format[unit_id],
                        'app': self.bundle,
                        'bannerType': self.get_ad_type('x.' + ad_format[unit_id]),
                        'platform': self.get_platform(self.is_android),
                        'account': f'Unity {"kids" if self.kids else "adults"}',
                        'GameID': str(game_id),
                        'mark': 'Bid',
                        'mediation': MediationTo1cConvertor.convert(self.mediation)
                    })
                )

        else:
            raise WrongMediationName

        data_base_to_send = MySql(
            host=DB_SENDER_HOST,
            user=DB_SENDER_USER,
            password=DB_SENDER_PASSWORD,
            db=DB_SENDER_NAME,
            port=DB_SENDER_PORT)

        for info in info_to_send:
            data_base_to_send.send_to_1c(
                ad_service=f'Unity {"kids" if self.kids else "adults"}',
                json=info,
                username=self._user_name
            )

        return True

# Unity(
#     ad_format=[AdFormats.reward, AdFormats.banner, AdFormats.inter],
#     bundle='com.movies.sfera',
#     age='5',
#     categories=['card', 'casino', 'alcoholicBeverages',
#                 'lotteryGambling', 'personalFinance', 'datingSocialMedia', 'dice',
#                 'lawGovernmentPolitics', 'realMoneyGambling'],
#     is_android=True,
#     kids=False,
#     mediation=Mediators.IS.value
# ).auto_writing()
