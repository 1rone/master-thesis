from Config.config import ADCOLONY_LOGIN, ADCOLONY_PASSWORD, DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, \
    DB_SENDER_NAME, DB_SENDER_PORT
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from TokensCollectors.AdServiceToken import AdServiceToken
from DataBase.MySql import MySql
from Exceptions.Exceptions import CannotGetToken
import time


class AdColonyToken(AdServiceToken):
    def __init__(self, kids=False):
        super().__init__()
        self.login = ADCOLONY_LOGIN
        self.password = ADCOLONY_PASSWORD
        self.kids = kids

    def get_token(self):
        sw_options = {
            'mitm_http2': False
        }

        service = Service()

        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(service=service,
                                  options=options,
                                  seleniumwire_options=sw_options)

        driver.get('https://clients.adcolony.com/login')

        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.ID, 'email'))).send_keys(self.login)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(self.password)

        time.sleep(15)

        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'link-login'))).click()

        driver.get('https://clients.adcolony.com/apps')

        time.sleep(6)

        if driver.current_url == 'https://clients.adcolony.com/login':
            raise Exception

        reqs = driver.requests

        for req in reversed(reqs):
            if 'template' in req.url:
                answer = req.headers
                break
        else:
            raise CannotGetToken

        driver.close()

        return [answer.get('Cookie'), answer.get('X-CSRF-Token')]

    def send_new_token(self):
        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            for token in self.get_token():
                print(data_base_to_send.send_header(ad_service='AdColony',
                                                    header_name='Cookie' if len(token) > 100 else 'X-CSRF-Token',
                                                    header_value=token))

            return 'Успішно оновлено токен для AdColony'
        except Exception:
            return 'Неуспішно AdColony, спробуй ще раз'


# AdColonyToken().get_token()
