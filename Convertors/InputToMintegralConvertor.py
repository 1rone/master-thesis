from Enums.Enums import MintegralMediators
from Exceptions.Exceptions import WrongMediationName


class InputToMintegralConvertor:
    @staticmethod
    def mediation_id(mediation: str) -> int:
        match mediation:
            case MintegralMediators.Others.value | MintegralMediators.CAS.value:
                return 0
            case MintegralMediators.MAX.value:
                return 1
            case MintegralMediators.Mopub.value:
                return 2
            case MintegralMediators.Admob.value:
                return 3
            case MintegralMediators.Fairbid.value:
                return 4
            case MintegralMediators.Tapdaq.value:
                return 5
            case MintegralMediators.Topon.value:
                return 6
            case MintegralMediators.Tradplus.value:
                return 7
            case MintegralMediators.Pangle.value:
                return 8
            case _:
                raise WrongMediationName
