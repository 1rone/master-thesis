import json
from AdServices.AdService import AdService
from AdServices.Mediators.IronSourceMediation import IronSource
from Config.config import DB_SENDER_HOST, DB_SENDER_NAME, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_PORT
from DataBase.MySql import MySql
from Enums.Enums import IronSourceAdNetworks, AdFormats, AdFormats1C
from User.User import User, current_user


class AdmobToIronSource(AdService):
    def __init__(self, app_id, instances, bundle: str, kids, account_name):
        super().__init__()
        self._user_name = User(current_user).get_1c_username()
        self.network_name = IronSourceAdNetworks.AdMob.value
        self.db = MySql(host=DB_SENDER_HOST,
                        db=DB_SENDER_NAME,
                        user=DB_SENDER_USER,
                        password=DB_SENDER_PASSWORD,
                        port=DB_SENDER_PORT)
        self.app_id = app_id
        self.instances = instances
        self.bundle = bundle
        self.kids = kids
        self.account_name = account_name
        self.is_android = False if bundle.isdigit() else True
        self.message = 'Успішно. '

    @staticmethod
    def get_ad_type(placement) -> str:
        match placement:
            case AdFormats.banner:
                return AdFormats1C.banner.name
            case AdFormats.inter:
                return AdFormats1C.inter.name
            case AdFormats.reward:
                return AdFormats1C.reward.name

    def auto_writing(self):

        is_info = {}

        if AdFormats.inter in self.instances:
            is_info['inter'] = self.instances.get(AdFormats.inter)

        if AdFormats.banner in self.instances:
            is_info['banner'] = self.instances.get(AdFormats.banner)

        if AdFormats.reward in self.instances:
            is_info['reward'] = self.instances.get(AdFormats.reward)

        IronSource(
            bundle=self.bundle,
            ad_format=[i for i in self.instances],
            taxonomy=None,
            kids=self.kids,
            is_android=self.is_android,
            app_config1=self.app_id,
            provider_name=IronSourceAdNetworks.AdMob.value,
            app_config2=None,
            instances=is_info
        ).add_mediation()

        info_to_send = []
        for unit in self.instances:
            letter = 'i' if unit == AdFormats.inter else 'b' if unit == AdFormats.banner else 'v'
            info_to_send.append(
                json.dumps({
                    'name':
                        ('a' if self.is_android else 'i') + f'.{letter}.bid.' + self.bundle + f' {self.account_name}',
                    'mark': 'Bid',
                    'PlacementID': self.instances[unit],
                    'app': self.bundle,
                    'bannerType': self.get_ad_type(unit),
                    'platform': self.get_platform(self.is_android),
                    'account': self.account_name,
                    'appId': self.app_id,
                    'mediation': 'is'
                })
            )

        for info in info_to_send:
            self.db.send_to_1c(
                ad_service=self.account_name,
                json=info,
                username=self._user_name
            )

        self.db.complete_task(bundle=self.bundle)

        return True, self.message
