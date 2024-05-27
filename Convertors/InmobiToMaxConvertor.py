from Enums.Enums import MaxAdFormats, MaxPlatforms
from Exceptions.Exceptions import WrongPlacementTypeException


class InmobiToMaxConvertor:

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
    def convert_platform(is_android: bool):
        match is_android:
            case False:
                return MaxPlatforms.ios
            case True:
                return MaxPlatforms.android
