import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from TokensCollectors.AdServiceToken import AdServiceToken
from DataBase.MySql import MySql
from Config.config import DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_NAME, MYTARGET_USER, \
    MYTARGET_PASSWORD, DB_SENDER_PORT
from Exceptions.Exceptions import CannotGetToken


class MyTargetToken(AdServiceToken):
    def __init__(self, kids=False):
        super().__init__()
        self.login = MYTARGET_USER
        self.password = MYTARGET_PASSWORD
        self.kids = kids

    def get_token(self):
        self.driver.get('https://target.my.com')

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]'))).click()

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(self.login)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(self.password)

        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[2]/div/div[4]/div[1]'))).click()

        time.sleep(2)

        self.driver.get('https://target.my.com/partner/groups')

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'flexi-table-nt__header__name-text')))

        time.sleep(10)
        reqs = self.driver.requests

        reqs.reverse()

        for req in reqs:
            if 'target' in req.url and 'api' in req.url and 'group_pads.json?fields=' in req.url:
                answer = req.headers
                break
        else:
            raise CannotGetToken

        self.driver.close()

        csrf = answer.get('Cookie')

        csrf = csrf[csrf.find('csrftoken=') + len('csrftoken='):]

        csrf = csrf[:csrf.find(';')]

        return [answer.get('Cookie'), csrf]

    def send_new_token(self):
        try:
            data_base_to_send = MySql(
                host=DB_SENDER_HOST,
                user=DB_SENDER_USER,
                password=DB_SENDER_PASSWORD,
                db=DB_SENDER_NAME,
                port=DB_SENDER_PORT)

            for token in self.get_token():
                print(data_base_to_send.send_header(ad_service='MyTarget',
                                                    header_name='Cookie' if len(token) > 100 else 'X-CSRFToken',
                                                    header_value=token))

            return 'Успішно оновлено токен для MyTarget'
        except Exception:
            return 'Неуспішно MyTarget, спробуй ще раз'
