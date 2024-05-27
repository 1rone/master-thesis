from Exceptions.Exceptions import WrongMediationName
from Enums.Enums import MaxAdNetworks as Max


class MaxAdNetworksInfo:

    def __init__(self, ad_network):
        match ad_network:
            case Max.AdColony:
                self.ApiName = 'ADCOLONY_NETWORK'
                self.ad_network_app_id = 'App ID'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Zone ID'
            case Max.Inmobi:
                self.ApiName = 'INMOBI_BIDDING'
                self.ad_network_app_id = 'App ID'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Placement ID'
            case Max.IronSource:
                self.ApiName = 'IRONSOURCE_NETWORK'
                self.ad_network_app_id = 'App Key'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Instance ID'
            case Max.Mintegral:
                self.ApiName = 'MINTEGRAL_BIDDING'
                self.ad_network_app_id = 'App ID'
                self.ad_network_app_key = 'App Key'
                self.ad_network_ad_unit_id = 'Ad Unit ID'
            case Max.MyTarget:
                self.ApiName = 'MYTARGET_BIDDING'
                self.ad_network_app_id = ''
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Slot ID'
            case Max.Pangle:
                self.ApiName = 'TIKTOK_BIDDING'
                self.ad_network_app_id = 'App ID'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Slot ID'
            case Max.TapJoy:
                self.ApiName = 'TAPJOY_NETWORK'
                self.ad_network_app_id = 'SDK Key'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Placement Name'
            case Max.Unity:
                self.ApiName = 'UNITY_NETWORK'
                self.ad_network_app_id = 'Game ID'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Placement ID'
            case Max.Vungle:
                self.ApiName = 'VUNGLE_BIDDING'
                self.ad_network_app_id = 'APP ID'
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Placement Reference ID'
            case Max.Yandex:
                self.ApiName = 'YANDEX_NETWORK'
                self.ad_network_app_id = ''
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = 'Block ID'
            case Max.MAX:
                self.ApiName = ''
                self.ad_network_app_id = ''
                self.ad_network_app_key = ''
                self.ad_network_ad_unit_id = ''
            case _:
                raise WrongMediationName

    def get_mediation_info(self, app_id=None, app_key=None, unit_id=None):
        answer = {'Api Name': self.ApiName}
        if app_id:
            self.change_ad_network_app_id(app_id)
            answer.update({'ad_network_app_id': self.ad_network_app_id})
        if app_key:
            self.change_ad_network_app_key(app_key)
            answer.update({'ad_network_app_key': self.ad_network_app_key})
        if unit_id:
            self.change_ad_network_ad_unit_id(unit_id)
            answer.update({'ad_network_ad_unit_id': self.ad_network_ad_unit_id})

        return answer

    def change_ad_network_app_id(self, app_id):
        self.ad_network_app_id = app_id

    def change_ad_network_app_key(self, app_key):
        self.ad_network_app_key = app_key

    def change_ad_network_ad_unit_id(self, unit_id):
        self.ad_network_ad_unit_id = unit_id
