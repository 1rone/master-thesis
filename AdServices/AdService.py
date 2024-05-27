from AdServices.AdServiceAbstract import AdServiceAbstract
from User.User import User, current_user
from Enums.Enums import AdFormats1C, Platforms1C, Mediators, Mediators1c


class AdService(AdServiceAbstract):
    _google_link = 'https://play.google.com/store/apps/details?id='
    _apple_link = 'https://apps.apple.com/us/app/rec-room/id'

    _user_name = User(current_user).get_1c_username()

    def __init__(self):
        pass

    def create_app(self):
        pass

    def auto_writing(self):
        pass

    @staticmethod
    def get_header(rows) -> dict:
        headers = {}
        for row in rows:
            headers.update(
                {row.get('HeaderName'): row.get('HeaderValue')}
            )
        return headers

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

    @staticmethod
    def get_mark(name, is_bid=True) -> str:
        if 'def' in name.lower() or 'bid' in name.lower():
            if is_bid:
                return 'Bid'
            else:
                return 'Def'
        else:
            return name[2:-1]

# AdService()
