from TokensCollectors.AdServiceTokenAbstract import AdServiceTokenAbstract
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from User.User import User, current_user


class AdServiceToken(AdServiceTokenAbstract):
    _selenium_path = User(current_user).get_selenium_path()

    def __init__(self):
        sw_options = {
            'mitm_http2': False
        }

        service = Service()

        options = webdriver.ChromeOptions()

        self.driver = webdriver.Chrome(service=service,
                                       options=options,
                                       seleniumwire_options=sw_options)

        self.driver.maximize_window()

    def get_token(self):
        pass

    def send_new_token(self):
        pass
