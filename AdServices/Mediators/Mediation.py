from abc import ABC

from User.User import User, current_user
from Enums.Enums import AdFormats1C, Platforms1C


class Mediation(ABC):

    _user_name = User(current_user).get_1c_username()
    _google_link = 'https://play.google.com/store/apps/details?id='
    _apple_link = 'https://apps.apple.com/us/app/rec-room/id'

    @staticmethod
    def get_ad_type(placement_id) -> str:
        match placement_id[2]:
            case 'i':
                return AdFormats1C.inter.name
            case 'v':
                return AdFormats1C.reward.name
            case _:
                return AdFormats1C.banner.name

    @staticmethod
    def get_platform(is_android) -> str:
        return Platforms1C.android.name if is_android else Platforms1C.ios.name

    def __init__(self):
        pass

    def add_mediation(self):
        pass
