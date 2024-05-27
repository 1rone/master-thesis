from Exceptions.Exceptions import WrongMediationName
from Enums.Enums import IronSourceAdNetworks as IS


class IronSourceAdNetworksInfo:

    def __init__(self, ad_network: IS, app_config: dict | None, instance_config: dict | None):
        self.provider_name = ad_network.value
        self.app_config = app_config
        self.instance_config = instance_config
        # match ad_network:
        #     case IS.AdColony:
        #         self.app_config = {'appID': app_config}
        #         self.instance_config = {'zoneId': instance_config}
        #     case IS.Inmobi:
        #         self.instance_config = {'placementId': instance_config}
        #         self.app_config = {}
        #     case IS.MyTarget:
        #         self.instance_config = {'slotId': instance_config,
        #                                 'PlacementID': instance_config}
        #         self.app_config = {}
        #     case IS.Pangle:
        #         self.app_config = {'appID': app_config}
        #         self.instance_config = {'slotID': instance_config}
        #     case IS.TapJoy:
        #         self.app_config = {'sdkKey': app_config,
        #                            'apiKey': app_config}
        #         self.instance_config = {'placementName': instance_config}
        #     case IS.Unity:
        #         self.app_config = {'sourceId': app_config}
        #         self.instance_config = {'zoneId': instance_config}
        #     case IS.Vungle:
        #         self.app_config = {'reportingAPIId': app_config,
        #                            'AppID': app_config}
        #         self.instance_config = {'PlacementId': instance_config}
        #     case _:
        #         raise WrongMediationName

    def get_mediation_info(self):
        answer = {
            "configurations": {
                self.provider_name: {
                    "rewardedVideo": [
                        {i: self.instance_config.get(i).get('reward') for i in self.instance_config}
                    ],
                    "interstitial": [
                        {i: self.instance_config.get(i).get('inter') for i in self.instance_config}
                    ],
                    "banner": [
                        {i: self.instance_config.get(i).get('banner') for i in self.instance_config}
                    ],
                    "appConfig": {i: self.app_config.get(i) for i in self.app_config}
                }
            }
        }
        return answer

    def get_output_dict(self):
        provider = {}

        if any('reward' in d for d in self.instance_config.values()):
            rewarded_video = [{i: self.instance_config.get(i).get('reward') for i in self.instance_config}]
            provider['rewardedVideo'] = rewarded_video

        if any('inter' in d for d in self.instance_config.values()):
            interstitial = [{i: self.instance_config.get(i).get('inter') for i in self.instance_config}]
            provider['interstitial'] = interstitial

        if any('banner' in d for d in self.instance_config.values()):
            banner = [{i: self.instance_config.get(i).get('banner') for i in self.instance_config}]
            provider['banner'] = banner

        if self.app_config:
            app_config_dict = {i: self.app_config.get(i) for i in self.app_config}
            provider['appConfig'] = app_config_dict

        return {'configurations': {self.provider_name: provider}}

    # def change_ad_network_app_id(self, app_id):
    #     self.ad_network_app_id = app_id
    #
    # def change_ad_network_app_key(self, app_key):
    #     self.ad_network_app_key = app_key
    #
    # def change_ad_network_ad_unit_id(self, unit_id):
    #     self.ad_network_ad_unit_id = unit_id

# IronSourceAdNetworksInfo(ad_network=IS.Vungle).get_mediation_info()
