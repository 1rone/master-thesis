from Enums.Enums import InmobiMediators
from Exceptions.Exceptions import WrongMediationName


class InputToInmobiConvertor:
    @staticmethod
    def mediation_id(mediation: str) -> int:
        match mediation:
            case InmobiMediators.Mopub.value:
                return 1
            case InmobiMediators.MAX.value:
                return 2
            case InmobiMediators.Amazon.value:
                return 3
            case InmobiMediators.Custom.value | InmobiMediators.CAS.value:
                return 5
            case InmobiMediators.IronSource.value:
                return 6
            case InmobiMediators.Springserve.value:
                return 7
            case InmobiMediators.Prebid.value:
                return 8
            case InmobiMediators.Fairbid.value:
                return 9
            case InmobiMediators.Admost.value:
                return 11
            case InmobiMediators.Aequus.value:
                return 12
            case InmobiMediators.Hyperbid.value:
                return 13
            case InmobiMediators.Meson.value:
                return 14
            case _:
                raise WrongMediationName
