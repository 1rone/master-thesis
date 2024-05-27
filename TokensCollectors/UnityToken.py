from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import pyotp
from TokensCollectors.AdServiceToken import AdServiceToken
from Exceptions.Exceptions import CannotGetToken
from DataBase.MySql import MySql
from Config.config import UNITY_ADULT_PASSWORD, UNITY_ADULT_USER, UNITY_KIDS_PASSWORD, UNITY_KIDS_USER, \
    DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_NAME, UNITY_KIDS_TOTP, UNITY_ADULTS_TOTP, \
    DB_SENDER_PORT


class UnityToken(AdServiceToken):
    def __init__(self, kids):
        super().__init__()
        self.kids = kids
        self.login = UNITY_KIDS_USER if kids else UNITY_ADULT_USER
        self.password = UNITY_KIDS_PASSWORD if kids else UNITY_ADULT_PASSWORD
        self.totp = UNITY_KIDS_TOTP if kids else UNITY_ADULTS_TOTP

    def get_totp(self):
        totp = pyotp.TOTP(self.totp)
        return totp.now()

    def get_token(self):
        self.driver.get('https://dashboard.unity3d.com/login?redirectTo=Lw==')
        time.sleep(2)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))).click()
        elements = self.driver.find_elements(By.CLASS_NAME, 'c2eaf9-MuiButtonBase-root')
        for element in elements:
            if element.text == 'Sign in':
                element.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.ID, "conversations_create_session_form_email"))).send_keys(self.login)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.NAME, "conversations_create_session_form[password]"))).send_keys(self.password)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.NAME, "commit"))).click()

        # TOTP Part
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'verify_code'))).send_keys(self.get_totp())
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.NAME, 'conversations_tfa_required_form[submit_verify_code]'))).click()
        except Exception:
            pass


        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-lyr6t7')))

        time.sleep(5)

        reqs = self.driver.requests
        for req in reqs:
            if 'unity' in req.url and 'monetize' in req.url and 's/me' in req.url:
                answer = req.headers
                break
        else:
            raise CannotGetToken

        self.driver.close()

        return answer.get('Authorization')

    def send_new_token(self):
        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            print(data_base_to_send.send_header(ad_service='Unity kids' if self.kids else 'Unity adults',
                                                header_name='Authorization',
                                                header_value=f'{self.get_token()}'))

            return 'Успішно оновлено токен для ' + ('Unity kids' if self.kids else 'Unity adults')
        except Exception:
            return 'Неуспішно ' + ('Unity kids' if self.kids else 'Unity adults') + ' спробуй ще раз'
# UnityToken(False).send_new_token()
