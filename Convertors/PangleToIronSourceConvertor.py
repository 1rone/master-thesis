from Enums.Enums import IronSourceAdFormats, AdFormats
from Exceptions.Exceptions import WrongPlacementTypeException


class PangleToIronSourceConvertor:
    @staticmethod
    def convert_ad_formats(placements):
        answer = []
        if AdFormats.inter in placements:
            answer.append(IronSourceAdFormats.INTER)
        if AdFormats.banner in placements:
            answer.append(IronSourceAdFormats.BANNER)
        if AdFormats.reward in placements:
            answer.append(IronSourceAdFormats.REWARD)

        if answer:
            return answer

        raise WrongPlacementTypeException

    @staticmethod
    def convert_coppa(coppa: int) -> bool:
        match coppa:
            case -1 | 0:
                return False
            case 1:
                return True
            case _:
                raise
