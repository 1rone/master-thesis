from Enums.Enums import AdFormats, AdFormats1C
from Exceptions.Exceptions import WrongPlacementTypeException


class InputTo1CConvertor:

    @staticmethod
    def ad_format(ad_format):
        match ad_format:
            case AdFormats.inter:
                return AdFormats1C.inter
            case AdFormats.reward:
                return AdFormats1C.reward
            case AdFormats.banner:
                return AdFormats1C.banner
            case _:
                raise WrongPlacementTypeException
