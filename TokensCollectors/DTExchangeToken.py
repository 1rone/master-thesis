from TokensCollectors.AdServiceToken import AdServiceToken
from Exceptions.Exceptions import CannotGetToken
from DataBase.MySql import MySql
from Config.config import DTEXCHANGE_LOGIN, DTEXCHANGE_PASSWORD, DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_USER, \
    DB_SENDER_HOST, DB_SENDER_PORT
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time


class DTExchangeToken(AdServiceToken):
    def __init__(self, kids=False):
        super().__init__()
        self.login = DTEXCHANGE_LOGIN
        self.password = DTEXCHANGE_PASSWORD
        self.kids = kids

    def get_token(self):
        self.driver.get('https://console.fyber.com/login')
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'username'))).send_keys(self.login)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'current-password'))).send_keys(self.password)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'signInSubmitButton'))).click()
        time.sleep(5)
        reqs = self.driver.requests
        answer = []
        for req in reqs:
            if 'fyber' in req.url and 'api' in req.url and 'me' in req.url:
                answer.append(req.headers)

        if not answer:
            raise CannotGetToken

        return answer[-1].get('Cookie')

    def send_new_token(self):
        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            print(data_base_to_send.send_header(
                ad_service='DTExchange',
                header_name='Cookie',
                header_value=self.get_token()))

        except Exception:
            return 'Неуспішно DTExchange, спробуй ще раз'

        return 'Успішно оновлено токен для DTExchange'
