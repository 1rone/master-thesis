from AdServices.AdService import AdService
from AdServices.Mediators.MaxMediation import MaxMediation
from Convertors.InputToMintegralConvertor import InputToMintegralConvertor
from DataBase.MySql import MySql
from Config.config import MINTEGRAL_SECRET, MINTEGRAL_SKEY, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import *
import time
import requests
import json
from Enums.Enums import AdFormats, MaxAdNetworks, MintegralMediators
from Convertors.MintegralToMaxConvertor import MintegralToMaxConvertor
from Convertors.MeditationTo1cConvertor import MediationTo1cConvertor


def get_int_time():
    return int(time.time())


def get_placement_name(is_android, ad_format):
    if is_android:
        answer = 'a._.bid'
    else:
        answer = 'i._.bid'
    match ad_format:
        case AdFormats.banner:
            answer = answer.replace('_', 'b')
        case AdFormats.reward:
            answer = answer.replace('_', 'v')
        case AdFormats.inter:
            answer = answer.replace('_', 'i')
        case _:
            raise WrongPlacementTypeException
    return answer


def get_ad_format_name(name):
    match name:
        case AdFormats.banner:
            return 'banner'
        case AdFormats.reward:
            return 'rewarded_video'
        case AdFormats.inter:
            return 'interstitial_video'
        case _:
            raise WrongPlacementTypeException


class Mintegral(AdService):

    def __init__(self, is_android, bundle, ad_format, coppa, orientation, mature, mediation):
        super().__init__()
        self.mediation = mediation
        self.skey = MINTEGRAL_SKEY
        self.secret = MINTEGRAL_SECRET
        self.is_android = is_android
        self.bundle = bundle
        self.link = (self._google_link if is_android else self._apple_link) + bundle
        self.ad_format = ad_format
        self.mature = mature
        self.coppa = coppa
        self.orientation = orientation
        self.app_key = '702a2f322dd9bc99d0e6cdfd9d026115'
        self.message = 'Успішно. '

    def get_token(self, timestamp):
        import hashlib
        secret = self.secret
        encoded_timestamp = hashlib.md5(str(timestamp).encode())
        token = secret + encoded_timestamp.hexdigest()
        md5_token = hashlib.md5(token.encode()).hexdigest()
        return md5_token

    def create_app(self):
        time_cur = get_int_time()
        url = 'https://dev.mintegral.com/app/open_api_create'
        params = {
            'skey': self.skey,
            'time': time_cur,
            'sign': self.get_token(time_cur)
        }
        params.update({'app_name': self.bundle,
                       'os': self.get_platform(self.is_android).upper(),
                       'package': self.bundle,
                       'is_live_in_store': '1',
                       'store_url': self.link,
                       'coppa': self.coppa,
                       'mediation_platform': InputToMintegralConvertor.mediation_id(self.mediation)})

        return requests.post(url=url, data=params).text

    def add_placements(self, app_id, placement_name, ad_type, orientation):
        time_cur = get_int_time()
        url = 'https://dev.mintegral.com/v2/placement/open_api_create'
        params = {
            'skey': self.skey,
            'time': time_cur,
            'sign': self.get_token(time_cur),
            'app_id': app_id
        }

        params.update({'placement_name': placement_name,
                       'ad_type': ad_type,
                       'integrate_type': 'sdk',
                       'package': self.bundle,
                       'video_orientation': orientation,
                       'show_close_button': 0,
                       'auto_fresh': 0,
                       'hb_unit_name': placement_name})
        result = requests.post(url=url, params=params).text
        print(result)
        return result

    def auto_writing(self):
        campaign_info = json.loads(self.create_app())
        # додати, якщо помилка
        if campaign_info['code'] == 200:
            info = []
            for ad_format in self.ad_format:
                info.append(
                    self.add_placements(
                        app_id=campaign_info['data']['app_id'],
                        placement_name=get_placement_name(self.is_android, ad_format),
                        ad_type=get_ad_format_name(ad_format),
                        orientation=self.orientation
                    ))

            for line in info:
                if json.loads(line)['code'] != 200:
                    raise ProblemsWithPlacementCreation

            info_to_send = []

            for unit in info:
                unit_info = json.loads(unit)
                info_to_send.append(
                    json.dumps({
                        'name': unit_info['data']['placement_name'] + '.' + self.bundle + ' Mintegral',
                        'appId': unit_info['data']['app_id'],
                        'app': self.bundle,
                        'bannerType': self.get_ad_type(unit_info['data']['placement_name']),
                        'platform': self.get_platform(self.is_android),
                        'account': 'Mintegral',
                        'placement': unit_info['data']['placement_id'],
                        'unit': unit_info['data']['unit_ids'][0],
                        'mark': self.get_mark(unit_info['data']['placement_name'], is_bid=True),
                        'mediation': MediationTo1cConvertor.convert(self.mediation)
                    })
                )

                if self.mediation == MintegralMediators.MAX.value:
                    try:
                        message = MaxMediation(
                            ad_format=MintegralToMaxConvertor.convert_ad_format(unit_info['data']['placement_name']),
                            platform=MintegralToMaxConvertor.convert_platform(is_android=self.is_android),
                            bundle=self.bundle,
                            kids=bool(self.coppa),
                            ad_network=MaxAdNetworks.Mintegral,
                            unit_id=unit_info['data']['unit_ids'][0],
                            app_key=self.app_key,
                            app_id=unit_info['data']['app_id'],
                            ad_network_optional_placement_id=unit_info['data']['placement_id']
                        ).add_mediation()
                        if message and len(info_to_send) == 1:
                            self.message += message
                        self.message += f'Додав у MAX {self.get_ad_type(unit_info["data"]["placement_name"])}. '
                    except Exception:
                        self.message += f'Не зміг додати в MAX {self.get_ad_type(unit_info["data"]["placement_name"])}. '

            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            for info in info_to_send:
                data_base_to_send.send_to_1c(
                    ad_service='Mintegral',
                    json=info,
                    username=self._user_name
                )

            if self.mature:
                self.message += 'Простав вручну mature. '
            if self.orientation != 'both':
                self.message += 'Простав вручну Direction Of Fullscreen Video. '

            return True, self.message

        else:
            raise AlreadyCreatedApp

# Mintegral(is_android=True,
#           bundle='net.gameo.roadlimits',
#           ad_format=[AdFormats.banner, AdFormats.inter, AdFormats.reward],
#           coppa=0,
#           mature=1,
#           orientation='both',
#           mediation=MintegralMediators.CAS.value).auto_writing()
