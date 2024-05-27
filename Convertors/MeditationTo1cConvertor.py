from Enums.Enums import Mediators, Mediators1c
from Exceptions.Exceptions import WrongMediationName


class MediationTo1cConvertor:

    @staticmethod
    def convert(mediation):
        match mediation:
            case Mediators.MAX.value:
                return Mediators1c.MAX.value
            case Mediators.CAS.value:
                return Mediators1c.CAS.value
            case Mediators.IS.value:
                return Mediators1c.IS.value
            case _:
                raise WrongMediationName
