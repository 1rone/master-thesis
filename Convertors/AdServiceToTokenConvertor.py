from Enums.Enums import AdServices
from TokensCollectors.UnityToken import UnityToken
from TokensCollectors.YandexToken import YandexToken
from TokensCollectors.InmobiToken import InmobiToken
from TokensCollectors.TapJoyToken import TapJoyToken
from TokensCollectors.AdColonyToken import AdColonyToken
from TokensCollectors.DTExchangeToken import DTExchangeToken
from TokensCollectors.MyTargetToken import MyTargetToken
from Exceptions.Exceptions import WrongAdService


class AdServiceToTokenConvertor:
    @staticmethod
    def convert(ad_service):
        match ad_service:
            case AdServices.UnityKids.value | AdServices.UnityAdults.value:
                return UnityToken
            case AdServices.Yandex.value:
                return YandexToken
            case AdServices.InmobiKids.value | AdServices.InmobiAdults.value:
                return InmobiToken
            # case AdServices.TapJoy.value:
            #     return TapJoyToken
            case AdServices.AdColony.value:
                return AdColonyToken
            case AdServices.DTExchange.value:
                return DTExchangeToken
            case AdServices.MyTarget.value:
                return MyTargetToken
            case _:
                raise WrongAdService

