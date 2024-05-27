import json
import requests
from Config.config import DB_APP_INFO_NAME, DB_APP_INFO_USER, DB_APP_INFO_PASSWORD, DB_APP_INFO_HOST, INTERNAL_TOKEN, \
    DB_SENDER_HOST, DB_SENDER_PASSWORD, DB_SENDER_PORT, DB_SENDER_NAME, DB_SENDER_USER
from DataBase.MySql import MySql
from Enums.Enums import AdFormats
from Exceptions.Exceptions import CannotFindApp


class AppInfoGetter:
    @staticmethod
    def get_ad_formats_and_ios_bundle(bundle):
        url = 'https://psvpromo.psvgamestudio.com/cas-app-info.php'
        params = {'id': bundle, 'platform': 1 if bundle.isdigit() else 0, 'key': INTERNAL_TOKEN}
        req = requests.get(url, params=params)
        ad_types = int(json.loads(req.text).get('adTypes'))
        ad_formats_mapping = [(AdFormats.reward, 4), (AdFormats.banner, 1), (AdFormats.inter, 2)]
        ad_formats = [fmt_enum for fmt_enum, flag in ad_formats_mapping if ad_types & flag]
        ios_package_id = json.loads(req.text).get('bundleName')
        return ad_formats, ios_package_id

    @staticmethod
    def get_info(bundle):
        data_base_getter = MySql(db=DB_APP_INFO_NAME, user=DB_APP_INFO_USER, password=DB_APP_INFO_PASSWORD,
                                 host=DB_APP_INFO_HOST)
        try:
            ad_formats, ios_package_id = AppInfoGetter.get_ad_formats_and_ios_bundle(bundle)
        except Exception:
            ad_formats = False
            ios_package_id = False

        if not ad_formats:
            line = data_base_getter.get_info_by_bundle(bundle)

            if line:
                ad_formats = [fmt_enum for fmt_enum, is_present in
                              [(AdFormats.banner, line['IsBanner']), (AdFormats.inter, line['IsInterstitial']),
                               (AdFormats.reward, line['IsRewarded'])] if is_present]
                ios_package_id = line['iOS_PackageId']
            else:
                raise CannotFindApp

        return {'is_android': not bundle.isdigit(), 'ad_format': ad_formats, 'ios_package_id': ios_package_id}

    @staticmethod
    def get_admob_info(bundle):
        data_base_getter = MySql(db=DB_SENDER_NAME, user=DB_SENDER_USER, password=DB_SENDER_PASSWORD,
                                 host=DB_SENDER_HOST, port=DB_SENDER_PORT)

        line = data_base_getter.get_admob_to_is(bundle)

        if line:

            ad_formats = {}

            if line['BannerBidId']:
                ad_formats[AdFormats.banner] = line['BannerBidId']

            if line['InterBidId']:
                ad_formats[AdFormats.inter] = line['InterBidId']

            if line['RewardedBidId']:
                ad_formats[AdFormats.reward] = line['RewardedBidId']

            app_id = line['AdmobAppId']
            account_name = line['AdmobAccountName']
        else:
            raise CannotFindApp

        return {'ad_format': ad_formats, 'app_id': app_id, 'account_name': account_name}

# Example usage
# app_info = AppInfoGetter.get_info('com.laplace.rabbington')
# print(app_info)
