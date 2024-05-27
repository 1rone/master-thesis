from Enums.Enums import TapjoyMaturity
from Exceptions.Exceptions import WrongMaturity


class FrontToTapjoyConvertor:
    @staticmethod
    def maturity(name: str):
        match name:
            case TapjoyMaturity.Mature.name:
                return TapjoyMaturity.Mature.value
            case TapjoyMaturity.High.name:
                return TapjoyMaturity.High.value
            case TapjoyMaturity.Medium.name:
                return TapjoyMaturity.Medium.value
            case TapjoyMaturity.Low.name:
                return TapjoyMaturity.Low.value
            case TapjoyMaturity.Everyone.name:
                return TapjoyMaturity.Everyone.value
            case _:
                raise WrongMaturity

    @staticmethod
    def categories(categories: [int]) -> [int]:

        if categories[1]:
            categories[1] = 2
        if categories[2]:
            categories[2] = 4
        if categories[3]:
            categories[3] = 16

        return list(filter(lambda x: x != 0, categories))
