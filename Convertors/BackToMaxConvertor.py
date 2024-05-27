from Enums.Enums import MaxPlatforms, MaxAdFormats, AdFormats
from Exceptions.Exceptions import WrongPlacementTypeException


class BackToMaxConvertor:

    @staticmethod
    def platform(is_android):
        match is_android:
            case True:
                return MaxPlatforms.android
            case False:
                return MaxPlatforms.ios

    @staticmethod
    def ad_format(ad_format):
        match ad_format:
            case AdFormats.inter:
                return MaxAdFormats.INTER
            case AdFormats.reward:
                return MaxAdFormats.REWARD
            case AdFormats.banner:
                return MaxAdFormats.BANNER
            case _:
                raise WrongPlacementTypeException
