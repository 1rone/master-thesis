from Enums.Enums import InmobiBlockedCategories
from Exceptions.Exceptions import WrongBlockedCategoriesName


class FrontToInmobiConvertor:

    @staticmethod
    def get_categories_id(name: str, kids: bool) -> int:
        match name:
            case InmobiBlockedCategories.Adults.value:
                return 0
            case InmobiBlockedCategories.Gambling.value:
                return 2528
            case InmobiBlockedCategories.Dating.value:
                return 2584
            case InmobiBlockedCategories.Teens.value:
                return 2586
            case InmobiBlockedCategories.Meedlight.value:
                return 2629
            case InmobiBlockedCategories.Mature.value:
                return 2585
            case _:
                if kids:
                    return 673
                else:
                    raise WrongBlockedCategoriesName

