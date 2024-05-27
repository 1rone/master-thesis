from enum import Enum, unique


class UserNames(Enum):
    Oleh = 'Олег'
    Vlad = 'Vlad'
    IrinaS = 'ИринаШлямович'
    SergT = 'СергейТубальцев'
    Liudmila = 'ХраброваЛюдмила'
    Natalia = 'НатальяНаумова'


class UserNamesPath(Enum):
    Oleh = "/Users/olehpetryshyn/auto-cas/chromedriver"
    Vlad = "C:/Users/Professional/Documents/auto-cas/chromedriver.exe"
    IrinaS = "C:/Users/irash/Downloads/chromedriver_win32/chromedriver.exe"
    SergT = "D:/BOT/chromedriver.exe"
    Liudmila = "C:/Users/Вкусняшка/Desktop/bot/chromedriver_win32/chromedriver.exe"
    Natalia = ""


@unique
class MaxAdNetworks(Enum):
    AdColony = 'AdColony'
    FairBid = 'FairBid'
    Inmobi = 'Inmobi'
    IronSource = 'IronSource'
    Mintegral = 'Mintegral'
    MyTarget = 'MyTarget'
    Pangle = 'Pangle'
    TapJoy = 'TapJoy'
    Unity = 'Unity'
    Vungle = 'Vungle'
    Yandex = 'Yandex'
    MAX = 'MAX'


@unique
class IronSourceAdNetworks(Enum):
    AdColony = 'adColony'
    Inmobi = 'inMobi'
    MyTarget = 'myTargetBidding'
    # TapJoy = 'TapJoyBidding'
    Pangle = 'pangle'
    Unity = 'unityAds'
    Vungle = 'liftoffMonetize'
    AdMob = 'googleAdMob'


@unique
class MaxAdFormats(Enum):
    BANNER = 'BANNER'
    INTER = 'INTER'
    REWARD = 'REWARD'


@unique
class IronSourceAdFormats(Enum):
    BANNER = 'banner'
    INTER = 'interstitial'
    REWARD = 'rewardedVideo'


# @unique
# class IronSourcePlatforms(Enum):
#     ios = ''


@unique
class MaxPlatforms(Enum):
    ios = 'ios'
    android = 'android'


@unique
class Platforms1C(Enum):
    ios = 'iOS'
    android = 'Android'


@unique
class AdFormats(Enum):
    reward = 'rewarded video'
    inter = 'interstitial'
    banner = 'banner'


@unique
class ChartBoostAdFormats(Enum):
    reward = 'rewarded'
    inter = 'interstitial'
    banner = 'banner'


@unique
class ChartBoostOrientations(Enum):
    portrait = ['portrait']
    landscape = ['landscape']
    both = ['portrait', 'landscape']


@unique
class AdFormats1C(Enum):
    reward = 'rewarded'
    inter = 'interstitial'
    banner = 'banner'


@unique
class InmobiBlockedCategories(Enum):
    Adults = 'Adults'
    Gambling = 'Gambling'
    Dating = 'Dating, Gambling, Prnography'
    Teens = 'Teens'
    Meedlight = 'Meedlight Filter'
    Mature = 'Mature'
    Kids = 'Kids'


@unique
class InmobiMediators(Enum):
    Mopub = 'Mopub Advanced Bidding'
    MAX = 'MAX'
    Amazon = 'Amazon TAM'
    Custom = 'Custom Mediation'
    IronSource = 'IS'
    Springserve = 'Springserve'
    Prebid = 'Prebid'
    Fairbid = 'DT Fairbid'
    Admost = 'Admost'
    Aequus = 'Aequus'
    Hyperbid = 'GameAnalytics Hyperbid'
    Meson = 'Meson'
    CAS = 'CAS'


@unique
class TapjoyMaturity(Enum):
    Mature = 5
    High = 4
    Medium = 3
    Low = 2
    Everyone = 1


@unique
class UnityBlockedCategories(Enum):
    Toddlers = 'Toddlers'
    Kids = 'Kids'
    Teens = 'Teens'
    Mature = 'Mature'
    Adults = 'Adults'


@unique
class AdColonyBlockedCategories(Enum):
    Pg = 'PG'
    Kids = 'Kids'
    Teens = 'Teens'
    Mature = 'Mature'
    Adults = 'Adults'


@unique
class MintegralMediators(Enum):
    Others = 'Others'
    CAS = 'CAS'
    MAX = 'MAX'
    Mopub = 'MoPub'
    Admob = 'AdMob'
    Fairbid = 'Fyber'
    Tapdaq = 'Tapdaq'
    Topon = 'TopOn'
    Tradplus = 'TradPlus'
    Pangle = 'Pangle'


@unique
class PangleCoppa(Enum):
    Kids = 'For Age 12 or under'
    Adults = 'For age 13+'
    Client = 'Client-side Configuration'


@unique
class PangleOrientation(Enum):
    Vertical = 'vertical'
    Horizontal = 'horizontal'


@unique
class PangleBlockCategories(Enum):
    Kids = 'Children'
    Teens = 'Teens up to 17+'
    Mature = 'Mature: азартных игр, алкоголя, знакомств, политики'
    Adults = 'Adult'


@unique
class AdServices(Enum):
    AdColony = 'AdColony'
    ChartBoost = 'ChartBoost'
    DTExchange = 'DTExchange'
    InmobiAdults = 'InmobiAdults'
    InmobiKids = 'InmobiKids'
    IronSourceAdults = 'IronSourceAdults'
    IronSourceKids = 'IronSourceKids'
    MaxAdults = 'MaxAdults'
    MaxKids = 'MaxKids'
    Mintegral = 'Mintegral'
    MyTargetAdults = 'MyTargetAdults'
    MyTargetKids = 'MyTargetKids'
    MyTarget = 'MyTarget'
    Pangle = 'Pangle'
    # TapJoy = 'TapJoy'
    UnityAdults = 'UnityAdults'
    UnityKids = 'UnityKids'
    VungleAdults = 'VungleAdults'
    VungleKids = 'VungleKids'
    Yandex = 'Yandex'


class IronSourceAdServicesAdditional(Enum):
    AdMob = 'AdMob'


@unique
class Mediators(Enum):
    CAS = 'CAS'
    IS = 'IS'
    MAX = 'MAX'


@unique
class Mediators1c(Enum):
    MAX = 'max'
    CAS = 'cas'
    IS = 'is'


@unique
class InmobiConsentOfAgeId(Enum):
    kids = 1
    teens = 3
    adults = 2
