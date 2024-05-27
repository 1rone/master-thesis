from Enums.Enums import AdFormats, IronSourceAdFormats
from Exceptions.Exceptions import WrongPlacementTypeException


class InputToIronSourceConvertor:

    @staticmethod
    def convert_ad_formats(placements):
        answer = []
        if AdFormats.inter in placements or IronSourceAdFormats.INTER in placements:
            answer.append(IronSourceAdFormats.INTER)
        if AdFormats.banner in placements or IronSourceAdFormats.BANNER in placements:
            answer.append(IronSourceAdFormats.BANNER)
        if AdFormats.reward in placements or IronSourceAdFormats.REWARD in placements:
            answer.append(IronSourceAdFormats.REWARD)

        if answer:
            return answer

        raise WrongPlacementTypeException
