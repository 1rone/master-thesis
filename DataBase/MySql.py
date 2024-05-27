import traceback
from DataBase.DataBase import DataBase
from Enums.Enums import UserNames
from Types.Types import mediationDict
from User.User import current_user


class MySql(DataBase):

    def send_header(self, ad_service, header_name, header_value):
        try:
            query = self.connection.cursor()
            query.execute(
                f'select * from parser.adservices_headers_collection where AdService = \'{ad_service}\''
                f' and HeaderName = \'{header_name}\'')
            if query.fetchall():
                query.execute(
                    f'Update parser.adservices_headers_collection Set HeaderValue = \'{header_value}\''
                    f' where AdService = \'{ad_service}\' and HeaderName = \'{header_name}\''
                )
            else:
                query.execute(
                    f'Insert into parser.adservices_headers_collection (Adservice, HeaderName, HeaderValue) VALUES'
                    f' (\'{ad_service}\', \'{header_name}\', \'{header_value}\')'
                )
            return True
        except Exception:
            return False




    def get_headers(self, ad_service, header_name):
        try:
            query = self.connection.cursor()
            query.execute(
                f'select * from parser.adservices_headers_collection where AdService = \'{ad_service}\''
                f' and HeaderName = \'{header_name}\'')
            rows = query.fetchall()
            return rows
        except Exception:
            return False

    def send_to_1c(self, ad_service: str, json, username: str) -> bool:
        try:
            query = self.connection.cursor()
            if current_user == UserNames.Oleh or current_user == UserNames.Vlad:
                table_name = 'parser.networks_1C_test'
            else:
                table_name = 'parser.networks_1C'
            query.execute(
                f'INSERT INTO {table_name} (AdServiceName, JsonData, USER) VALUES (\'{ad_service}\', \'{json}\', \'{username}\')')
        except Exception:
            return False
        return True

    def complete_task(self, bundle) -> bool:
        try:
            query = self.connection.cursor()
            query.execute(
                f'UPDATE parser.ads_admob_to_is SET isComplete = 1 WHERE BundleId = %s', args=bundle
            )
        except Exception:
            return False
        return True

    def send_mediation_info(self, info: mediationDict):
        try:
            row = 'INSERT INTO parser.mediation_info (MediationName, MyBundle, MediationBundle, BannerType, AppId, PlacementId) VALUES'
            for bannerType in info:
                row += f' (\'{info.get(bannerType).get("mediationName")}\', \'{info.get(bannerType).get("myBundle")}\', \'{info.get(bannerType).get("mediationBundle")}\', \'{bannerType}\', \'{info.get(bannerType).get("AppId")}\', \'{info.get(bannerType).get("PlacementId")}\'),'
            row = row[:-1] + ';'
            query = self.connection.cursor()
            query.execute(row)
        except Exception:
            print(traceback.format_exc())
            return False
        return True

    def get_mediation_info(self, mediation, bundle, banner_type):
        try:
            query = self.connection.cursor()
            if banner_type:
                query.execute(
                    f'SELECT * FROM parser.mediation_info where MediationName = \'{mediation}\' and MediationBundle = \'{bundle}\' and BannerType = \'{banner_type}\' ORDER BY Id DESC')
            else:
                query.execute(
                    f'SELECT * FROM parser.mediation_info where MediationName = \'{mediation}\' and MediationBundle = \'{bundle}\' ORDER BY Id DESC')
            rows = query.fetchone()
            return rows
        except Exception:
            return False

    def get_admob_to_is(self, bundle):
        try:
            query = self.connection.cursor()
            query.execute(
                'SELECT * FROM parser.ads_admob_to_is where BundleId = %s ORDER BY id DESC', args=bundle
            )
            rows = query.fetchone()
            return rows
        except Exception:
            return False

    # def send_task(self, ad_service, categories: str, bundle) -> bool:
    #     try:
    #         query = self.connection.cursor()
    #         query.execute(
    #             f'INSERT INTO parser.auto_task_manager (Bundle, AdService, Categories, Status) VALUES'
    #             f' (\'{bundle}\', \'{ad_service}\', \'{categories}\', 0)')
    #
    #     except Exception:
    #         print(traceback.format_exc())
    #         return False
    #     return True
    #
    # def get_unfinished_tasks(self) -> list:
    #     try:
    #         query = self.connection.cursor()
    #         query.execute('Select * from parser.auto_task_manager WHERE Status = 0')
    #         lines = query.fetchall()
    #         return lines
    #     except Exception:
    #         pass
    #
    # def finish_task(self, bundle):
    #     try:
    #         query = self.connection.cursor()
    #         query.execute(f'UPDATE parser.auto_task_manager SET Status = 1 WHERE Bundle = \'{bundle}\''
    #                       f' ORDER BY ID DESC LIMIT 1')
    #     except Exception:
    #         pass
    #
    # def unsuccessful_task(self, bundle):
    #     try:
    #         query = self.connection.cursor()
    #         query.execute(f'UPDATE parser.auto_task_manager SET Status = -1 WHERE Bundle = \'{bundle}\' AND'
    #                       f' Status = 0 ORDER BY ID DESC LIMIT 1')
    #         # query.execute(f'UPDATE parser.auto_task_manager SET Status = -1 WHERE Bundle = \'{bundle}\' DESC LIMIT 1')
    #     except Exception:
    #         pass
    #
    # def add_user_to_telegram(self, tg_id):
    #     try:
    #         query = self.connection.cursor()
    #         query.execute(
    #             f'INSERT INTO parser.auto_task_manager_telegram_users (tg_id) VALUE ({tg_id})'
    #         )
    #     except Exception:
    #         pass
    #
    # def get_telegram_managers(self):
    #     try:
    #         query = self.connection.cursor()
    #         query.execute(
    #             f'SELECT * FROM parser.auto_task_manager_telegram_users'
    #         )
    #         lines = query.fetchall()
    #         return [line['tg_id'] for line in lines]
    #     except Exception:
    #         pass

    def get_info_by_bundle(self, bundle_id):
        query = self.connection.cursor()
        query.execute(
            f'select Platform_ID, Name, IsBanner, IsInterstitial, IsRewarded, iOS_PackageId from Applications'
            f' left join Applications_Setup on Applications.App_ID = Applications_Setup.App_Id'
            f' where Bundle_ID = \'{bundle_id}\'')
        row = query.fetchone()
        return row
