from Enums.Enums import MaxPlatforms, MaxAdFormats, TapjoyMaturity
from Exceptions.Exceptions import WrongPlacementTypeException, WrongMaturity


class TapJoyToMaxConvertor:
    @staticmethod
    def convert_ad_format(placement):
        match placement[2]:
            case 'i':
                return MaxAdFormats.INTER
            case 'v':
                return MaxAdFormats.REWARD
            case 'b':
                return MaxAdFormats.BANNER
            case _:
                raise WrongPlacementTypeException

    @staticmethod
    def convert_platform(is_android: bool) -> MaxPlatforms:
        match is_android:
            case False:
                return MaxPlatforms.ios
            case True:
                return MaxPlatforms.android

    @staticmethod
    def convert_maturity(maturity: int) -> bool:
        match maturity:
            case TapjoyMaturity.Mature.value | TapjoyMaturity.High.value | TapjoyMaturity.Medium.value:
                return False
            case TapjoyMaturity.Low.value | TapjoyMaturity.Everyone.value:
                return True
            case _:
                raise WrongMaturity
