from Enums.Enums import IronSourceAdFormats, TapjoyMaturity, AdFormats
from Exceptions.Exceptions import WrongPlacementTypeException, WrongMaturity


class TapJoyToIronSourceConvertor:
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
    def convert_maturity(maturity: int) -> bool:
        match maturity:
            case TapjoyMaturity.Mature.value | TapjoyMaturity.High.value | TapjoyMaturity.Medium.value:
                return False
            case TapjoyMaturity.Low.value | TapjoyMaturity.Everyone.value:
                return True
            case _:
                raise WrongMaturity
