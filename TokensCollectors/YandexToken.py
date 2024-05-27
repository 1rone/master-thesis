import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from TokensCollectors.AdServiceToken import AdServiceToken
from DataBase.MySql import MySql
from Config.config import YANDEX_LOGIN, YANDEX_PASSWORD, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from Exceptions.Exceptions import CannotGetToken
import traceback


class YandexToken(AdServiceToken):

    def __init__(self, kids=False):
        super().__init__()
        self.login = YANDEX_LOGIN
        self.password = YANDEX_PASSWORD
        self.kids = kids

    def get_token(self):
        self.driver.get('https://passport.yandex.ru/auth')
        time.sleep(3)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="passp-field-login"]'))) \
            .send_keys(self.login)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passp:sign-in"]'))).click()
        time.sleep(3)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="passp-field-passwd"]'))).send_keys(self.password)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passp:sign-in"]'))).click()
        time.sleep(5)
        self.driver.get('https://partner.yandex.ru/v2/inapp/app')
        self.driver.get('https://partner.yandex.ru/v2/inapp/app')
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/header/div/div/div[2]/div[3]/div/div/a[1]/span[1]')))
        time.sleep(10)
        reqs = self.driver.requests
        reqs.reverse()
        for req in reqs:
            if 'yandex' in req.url and 'click' in req.url:
                answer = req.headers
                break
        else:
            raise CannotGetToken
        self.driver.close()
        return answer.get('Cookie')

    def send_new_token(self):
        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            print(data_base_to_send.send_header(
                ad_service='Yandex',
                header_name='Cookie',
                header_value=self.get_token()))

        except Exception:
            print(traceback.print_exc())
            return 'Неуспішно Yandex, спробуй ще раз'

        return 'Успішно оновлено токен для Yandex'

# YandexToken().send_new_token()
