from Enums.Enums import AdColonyBlockedCategories
from Exceptions.Exceptions import WrongBlockedCategoriesName


class FrontToAdcolonyConvertor:
    @staticmethod
    def get_categories_list(category: str) -> [int]:
        match category:
            case AdColonyBlockedCategories.Pg.value:
                return [4, 5, 8, 12, 16, 17, 20, 21, 23, 25, 26, 27, 28, 29, 31, 40]
            case AdColonyBlockedCategories.Kids.value:
                return [4, 5, 6, 8, 9, 12, 13, 16, 17, 20, 21, 23, 25, 26, 27, 28, 29, 31, 40]
            case AdColonyBlockedCategories.Teens.value:
                return [4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 23, 25, 26, 27, 28, 29, 31, 40]
            case AdColonyBlockedCategories.Mature.value:
                return [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 20, 21, 23, 25, 26, 27, 28, 29, 31, 35, 36,
                        37, 40]
            case AdColonyBlockedCategories.Adults.value:
                return [i + 1 for i in range(40)]
            case _:
                raise WrongBlockedCategoriesName
