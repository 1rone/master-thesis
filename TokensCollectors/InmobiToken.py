import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from TokensCollectors.AdServiceToken import AdServiceToken
from Config.config import INMOBI_KIDS_LOGIN, INMOBI_KIDS_PASSWORD, INMOBI_ADULTS_LOGIN, INMOBI_ADULTS_PASSWORD, \
    DB_SENDER_PASSWORD, DB_SENDER_NAME, DB_SENDER_USER, DB_SENDER_HOST, DB_SENDER_PORT
from Exceptions.Exceptions import CannotGetToken
from DataBase.MySql import MySql
import traceback


class InmobiToken(AdServiceToken):

    def __init__(self, kids):
        super().__init__()
        self.login = INMOBI_KIDS_LOGIN if kids else INMOBI_ADULTS_LOGIN
        self.password = INMOBI_KIDS_PASSWORD if kids else INMOBI_ADULTS_PASSWORD
        self.kids = kids

    def get_token(self):
        self.driver.get('https://publisher.inmobi.com')
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="app"]/div/div/div[5]/div[1]'
                          '/div/div/div[2]/div/div/div/div[1]/div/div/div/button[1]'))).click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(self.login)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'btn-next'))).click()
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'password'))).send_keys(self.password)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'btn-login'))).click()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((
                By.XPATH,
                '/html/body/div[1]/div/div/div[5]/div[1]/div/div[1]/div/div/nav/ul/li[1]/a/span[2]')))
        time.sleep(5)
        reqs = self.driver.requests
        answer = []
        for req in reqs:
            if 'publisher' in req.url and 'api' in req.url and 'graphql' in req.url:
                answer.append(req.headers)

        if not answer:
            raise CannotGetToken

        return [answer[-1].get('x-tk'), answer[-1].get('Cookie')]

    def send_new_token(self):
        try:
            tokens = self.get_token()
            for token in tokens:
                data_base_to_send = MySql(
                    host=DB_SENDER_HOST,
                    user=DB_SENDER_USER,
                    password=DB_SENDER_PASSWORD,
                    db=DB_SENDER_NAME,
                    port=DB_SENDER_PORT)

                print(data_base_to_send.send_header(ad_service='Inmobi ' + ('kids' if self.kids else 'adults'),
                                                    header_name='x-tk' if len(token) < 100 else 'Cookie',
                                                    header_value=f'{token}'))
        except Exception:
            print(traceback.print_exc())
            return 'Неуспішно Inmobi ' + ('kids' if self.kids else 'adults') + ', спробуй ще раз'
        return 'Успішно оновлено токени для Inmobi ' + ('kids' if self.kids else 'adults')

# print(InmobiToken(kids=False).send_new_token())
