from Enums.Enums import PangleCoppa, PangleOrientation, PangleBlockCategories
from Exceptions.Exceptions import WrongCoppaName, WrongOrientationName, WrongBlockedCategoriesName


class FrontToPangleConvertor:
    @staticmethod
    def get_coppa_id(name: str) -> int:
        match name:
            case PangleCoppa.Kids.value:
                return 1
            case PangleCoppa.Adults.value:
                return 0
            case PangleCoppa.Client.value:
                return -1
            case _:
                raise WrongCoppaName

    @staticmethod
    def get_orientation_id(name: str) -> int:
        match name:
            case PangleOrientation.Vertical.value:
                return 1
            case PangleOrientation.Horizontal.value:
                return 2
            case _:
                raise WrongOrientationName

    @staticmethod
    def get_block_cat_id(name) -> int:
        match name:
            case PangleBlockCategories.Kids.value:
                return 523256
            case PangleBlockCategories.Teens.value:
                return 523208
            case PangleBlockCategories.Mature.value:
                return 523207
            case PangleBlockCategories.Adults.value:
                return 0
            case _:
                raise WrongBlockedCategoriesName
