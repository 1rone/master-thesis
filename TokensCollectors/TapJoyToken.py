from TokensCollectors.AdServiceToken import AdServiceToken
from Config.config import TAPJOY_LOGIN, TAPJOY_PASSWORD, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from DataBase.MySql import MySql
import time
from Exceptions.Exceptions import *


class TapJoyToken(AdServiceToken):
    def __init__(self, kids=False):
        super().__init__()
        self.login = TAPJOY_LOGIN
        self.password = TAPJOY_PASSWORD
        self.kids = kids

    def get_token(self):
        self.driver.get('https://ltv.tapjoy.com')

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(self.login)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(self.password)

        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'session_btn_primary'))).click()

        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'table_cell')))

        time.sleep(6)
        reqs = self.driver.requests

        for req in reqs:
            if 'ltv' in req.url and 'tapjoy' in req.url and 'app_groups' in req.url:
                answer = req.headers
                break
        else:
            raise CannotGetToken

        return [answer.get('Cookie'), answer.get('X-NewRelic-ID')]

    def send_new_token(self):

        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            for token in self.get_token():
                print(data_base_to_send.send_header(ad_service='TapJoy',
                                                    header_name='Cookie' if len(token) > 100 else 'X-NewRelic-ID',
                                                    header_value=token))

            return 'Успішно оновлено токен для TapJoy'
        except Exception:
            return 'Неуспішно TapJoy, спробуй ще раз'


# TapJoyToken().send_new_token()
