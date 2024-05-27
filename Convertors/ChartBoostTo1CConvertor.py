from Enums.Enums import AdFormats, ChartBoostAdFormats
from Exceptions.Exceptions import WrongPlacementTypeException


class ChartBoostTo1CConvertor:

    @staticmethod
    def ad_format(ad_format):
        match ad_format:
            case AdFormats.inter:
                return ChartBoostAdFormats.inter
            case AdFormats.reward:
                return ChartBoostAdFormats.reward
            case AdFormats.banner:
                return ChartBoostAdFormats.banner
            case _:
                raise WrongPlacementTypeException
