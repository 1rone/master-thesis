from AdServices.BlockedCategories.UnityCategoriesName import UnityBlockedCategories as ubc
from Enums.Enums import UnityBlockedCategories
from Exceptions.Exceptions import WrongBlockedCategoriesName


class FrontToUnityConvertor:
    @staticmethod
    def get_categories(category_name: str) -> str:
        match category_name:
            case UnityBlockedCategories.Toddlers.value:
                return ubc().get_toddlers()

            case UnityBlockedCategories.Kids.value:
                return ubc().get_kids()

            case UnityBlockedCategories.Teens.value:
                return ubc().get_teens()

            case UnityBlockedCategories.Mature.value:
                return ubc().get_mature()

            case UnityBlockedCategories.Adults.value:
                return ubc().get_adults()

            case _:
                raise WrongBlockedCategoriesName
