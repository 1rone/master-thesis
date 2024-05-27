from abc import ABC, abstractmethod
from User.User import User, current_user


class AdServiceTokenAbstract(ABC):
    _selenium_path = User(current_user).get_selenium_path()

    # _selenium_path = "C:/Users/Professional/Desktop/autoCas/chromedriver.exe"

    # _selenium_path = "C:/Users/Ира/Downloads/chromedriver_win32/chromedriver.exe"

    # _selenium_path = "D:\BOT\chromedriver.exe"

    # _selenium_path = "/Users/olehpetryshyn/auto-cas/chromedriver"

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_token(self):
        pass

    @abstractmethod
    def send_new_token(self):
        pass
