from Enums.Enums import UserNames, UserNamesPath
from Exceptions.Exceptions import WrongUser
import os


class User:
    def __init__(self, username: UserNames):
        self.username = username

    def get_selenium_path(self):
        match self.username:
            case UserNames.Oleh:
                return UserNamesPath.Oleh.value
            case UserNames.Vlad:
                return UserNamesPath.Vlad.value
            case UserNames.IrinaS:
                return UserNamesPath.IrinaS.value
            case UserNames.SergT:
                return UserNamesPath.SergT.value
            case UserNames.Liudmila:
                return UserNamesPath.Liudmila.value
            case UserNames.Natalia:
                return UserNamesPath.Natalia.value
            case _:
                raise WrongUser

    def get_1c_username(self):
        return self.username.value


def get_current_user():
    path = os.path.dirname(os.path.realpath(__file__))
    print(f'I am running on {path}')
    if 'oleh' in path:
        return UserNames.Oleh
    elif 'User 1' in path:
        return UserNames.Oleh
    elif 'Professional' in path:
        return UserNames.Vlad
    elif 'Taganov' in path:
        return UserNames.SergT
    elif 'irash' in path:
        return UserNames.IrinaS
    elif 'Вкусняшка' in path:
        return UserNames.Liudmila
    elif 'Temp' in path:
        return UserNames.Natalia
    else:
        raise WrongUser


current_user = get_current_user()
