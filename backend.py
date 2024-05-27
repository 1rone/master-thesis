import traceback
from AdServices.AdColony import AdColony
from Config.config import DB_SENDER_HOST, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_USER, DB_SENDER_PORT
from DataBase.MySql import MySql
from Exceptions.Exceptions import *
from AdServices.DTExchange import DTExchange
from AdServices.Inmobi import Inmobi
from AdServices.Mediators.IronSourceMediation import IronSource
from AdServices.Mintegral import Mintegral
from AdServices.MyTarget import MyTarget
from AdServices.Pangle import Pangle
from AdServices.Unity import Unity
from AdServices.Vungle import Vungle
from AdServices.Yandex import Yandex
from AdServices.ChartBoost import CharBoost
from Enums.Enums import AdServices, MaxAdNetworks, IronSourceAdServicesAdditional
from AppInfoGetter import AppInfoGetter
from AdServices.BridgeApps.AdMobToIronSource import AdmobToIronSource
from AdServices.Mediators.MaxMediation import MaxMediation
from Convertors.BackToMaxConvertor import BackToMaxConvertor
from Convertors.InputToIronSourceConvertor import InputToIronSourceConvertor


def is_kids(ad_service):
    return True if 'kids' in ad_service.lower() else False


def unit_auto_creating(bundle: str,
                       ad_service: str,
                       mediator: str,
                       age: str = '5',
                       categories=None,
                       coppa: int = 0,
                       mature: int = 0,
                       orientation: str = 'both',
                       app_category: int or str = 0,
                       category_id: int = 0,
                       trash: str = ''):
    try:
        if mediator == 'IS' and 'ironsource' not in ad_service.lower():
            if not MySql(host=DB_SENDER_HOST,
                         db=DB_SENDER_NAME,
                         user=DB_SENDER_USER,
                         password=DB_SENDER_PASSWORD,
                         port=DB_SENDER_PORT).get_mediation_info(mediation='IS',
                                                                 bundle=bundle,
                                                                 banner_type=None):
                return 'Спочатку потрібно додати цей бандл в Айронсорс'
        if mediator == 'IS' and 'admob' in ad_service.lower():
            info = AppInfoGetter.get_admob_info(bundle=bundle)
            checker = False
        else:
            checker = True
            info = AppInfoGetter.get_info(bundle=bundle)
    except CannotFindApp:
        return 'Такого бандлу немає в базі даних'
    except CannotFindAppInDbCleverAdsSolutions:
        return 'Це не клієнтський додаток. Не можу опрацювати цей бандл'

    try:
        if checker:
            if not info.get('is_android'):
                if not info.get('ios_package_id'):
                    raise EmptyIos1CBundleException

        kids = is_kids(ad_service=ad_service)

        match ad_service:

            case AdServices.MyTargetKids.value | AdServices.MyTargetAdults.value:
                status, message = MyTarget(bundle=bundle,
                                           is_android=info.get('is_android'),
                                           ad_format=info.get('ad_format').copy(),
                                           categories=categories,
                                           mediation=mediator,
                                           kids=kids).auto_writing()
                if status:
                    return message

                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            case IronSourceAdServicesAdditional.AdMob.value:
                status, message = AdmobToIronSource(
                    bundle=bundle,
                    kids=True if coppa else False,
                    app_id=info.get('app_id'),
                    instances=info.get('ad_format'),
                    account_name=info.get('account_name')
                ).auto_writing()

                if status:
                    return message

                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            case AdServices.UnityKids.value | AdServices.UnityAdults.value:
                if Unity(bundle=bundle,
                         is_android=info.get('is_android'),
                         ad_format=info.get('ad_format').copy(),
                         categories=categories,
                         age=age,
                         kids=kids,
                         mediation=mediator
                         ).auto_writing():
                    return 'Успішно'

                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case AdServices.Mintegral.value:

                status, message = Mintegral(
                    bundle=bundle,
                    is_android=info.get('is_android'),
                    ad_format=info.get('ad_format').copy(),
                    coppa=coppa,
                    mature=mature,
                    orientation=orientation,
                    mediation=mediator
                ).auto_writing()

                if status:
                    return message
                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case AdServices.DTExchange.value:
                if DTExchange(
                        bundle=bundle,
                        is_android=info.get('is_android'),
                        ad_formats=info.get('ad_format').copy(),
                        kids=True if coppa else False).auto_writing():
                    return 'Успішно'
                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            case AdServices.Yandex.value:

                if Yandex(
                        bundle=bundle,
                        is_android=info.get('is_android'),
                        ad_format=info.get('ad_format').copy(),
                        mediation=mediator
                ).auto_writing():
                    return 'Успішно'
                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            case AdServices.AdColony.value:

                status, message = AdColony(
                    bundle=bundle,
                    is_android=info.get('is_android'),
                    ad_format=info.get('ad_format').copy(),
                    coppa=coppa,
                    categories=categories,
                    mediation=mediator
                ).auto_writing()

                if status:
                    return message
                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            # case AdServices.TapJoy.value:
            #
            #     status, message = TapJoy(bundle=bundle,
            #                              ad_format=info.get('ad_format').copy(),
            #                              is_android=info.get('is_android'),
            #                              categories=categories,
            #                              maturity=mature,
            #                              orientation=orientation,
            #                              mediation=mediator
            #                              ).auto_writing()
            #     if status:
            #         return message
            #     else:
            #         return 'Неуспішно. Потрібно перевірити та видалити'

            case AdServices.VungleKids.value | AdServices.VungleAdults.value:

                status, message = Vungle(bundle=bundle,
                                         is_android=info.get('is_android'),
                                         ad_format=info.get('ad_format').copy(),
                                         kids=kids,
                                         mediation=mediator
                                         ).auto_writing()
                if status:
                    return message
                else:
                    return 'Неуспішно. Потрібно перевірити та видалити'

            case AdServices.MaxKids.value | AdServices.MaxAdults.value:

                for ad_format in info.get('ad_format').copy():
                    if not MaxMediation(
                            kids=kids,
                            platform=BackToMaxConvertor.platform(info.get('is_android')),
                            ad_format=BackToMaxConvertor.ad_format(ad_format),
                            ad_network=MaxAdNetworks.MAX,
                            app_key=None,
                            app_id=None,
                            unit_id=None,
                            bundle=bundle
                    ).create_placement():
                        return 'Неуспішно, Потрібно перевірити та видалити'
                if kids:
                    return 'Успішно. Потрібно включити в MAX AdFiltering'
                else:
                    return 'Успішно'

            case AdServices.InmobiKids.value | AdServices.InmobiAdults.value:

                status, message = Inmobi(bundle=bundle,
                                         is_android=info.get('is_android'),
                                         ad_format=info.get('ad_format').copy(),
                                         categories_id=categories,
                                         mediation=mediator,
                                         kids=kids,
                                         consent_of_age=mature,
                                         ).auto_writing()
                if status:
                    return message
                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case AdServices.Pangle.value:

                status, message = Pangle(bundle=bundle,
                                         is_android=info.get('is_android'),
                                         ad_format=info.get('ad_format').copy(),
                                         app_category=app_category,
                                         block_category_id=[category_id],
                                         coppa=coppa,
                                         orientation=orientation,
                                         mediation=mediator
                                         ).auto_writing()
                if status:
                    return message

                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case AdServices.ChartBoost.value:

                status, message = CharBoost(bundle=bundle,
                                            is_android=info.get('is_android'),
                                            ad_formats=info.get('ad_format').copy(),
                                            kids=True if coppa else False,
                                            orientations=orientation,
                                            store_app_id=bundle if info.get('is_android') else info.get('ios_package_id')
                                            ).auto_writing()
                if status:
                    return message

                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case AdServices.IronSourceKids.value | AdServices.IronSourceAdults.value:

                if IronSource(bundle=bundle,
                              is_android=info.get('is_android'),
                              ad_format=info.get('ad_format').copy(),
                              kids=kids,
                              taxonomy=app_category
                              ).create_app():
                    return 'Успішно'

                else:
                    return 'Неуспішно, Потрібно перевірити та видалити'

            case _:
                raise NotSelectedAdService

    except (WrongToken, CannotGetToken) as error:
        print(error)
        return 'Неуспішно. Потрібно оновити токен'

    except EmptyIos1CBundleException:
        return 'Не заповнено текстовий бандл цього додатку в 1с'

    except WrongPlacementTypeException:
        return 'Неуспішно. Не правильний тип плейсменту'

    except CannotFindApp:
        return f'Неуспішно. {ad_service} не може знайти цей додаток у сторі'

    except AlreadyCreatedApp:
        return 'Неуспішно. Такий додаток вже створено'

    except WrongStatusCode as err:
        return f'Неуспішно. Потрібно оновити токен та перевірити на сайті. {err}'

    except ProblemsWithPlacementCreation:
        return 'Неуспішно. Не зміг створити плейсменти. Дороби додаток вручну'

    except CannotCreateApp:
        return 'Неуспішно. Не вдалося створити додаток, спробуй ще раз'

    except CannotGetPlacementId:
        return 'Неуспішно. Не зміг знайти плейсмент. Дороби вручну'

    except CannotGetAppId:
        return 'Неуспішно. Не зміг знайти такий додаток'

    except CannotGetCategories:
        return 'Неуспішно. Не зміг знайти категорію додатку. Заповни вручну'

    except WrongInternalCode:
        return 'Неуспішно. Перевір що пише в консолі'

    except AlreadyCreatedPlacement:
        return 'Неуспішно. Такий плейсмент вже створено'

    except WrongTaxonomy:
        return 'Неуспішно. Проблема з категорією додатку. Дьоргай програміста'

    except ChartBoostPlacementsException:
        return 'Неуспішно. В Чартбусті дитячому баннер не працює'

    except NotAddedInIronSource:
        return 'Спочатку потрібно додати цей бандл в Айронсорс'

    except NotSelectedAdService:
        print(traceback.format_exc())
        return 'Не вибрано рекламну мережу'

    except NotSelectedAdFormats:
        return 'Не вибрано жодного відповідного формату реклами'

    except ConnectionError:
        return 'Не можу під\'єднатися до мережі'

    except Exception as err:
        print('err=', err)
        print(traceback.format_exc())
        return 'Невідома помилка, оброби бандл вручну'
