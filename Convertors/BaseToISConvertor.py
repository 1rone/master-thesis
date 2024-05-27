from Enums.Enums import IronSourceAdFormats
from Exceptions.Exceptions import WrongPlacementTypeException


class BaseToISConvertor:

    @staticmethod
    def ad_format(ad_format):
        match ad_format:
            case 'banner':
                return IronSourceAdFormats.BANNER.value
            case 'reward':
                return IronSourceAdFormats.REWARD.value
            case 'inter':
                return IronSourceAdFormats.INTER.value
            case _:
                raise WrongPlacementTypeException
