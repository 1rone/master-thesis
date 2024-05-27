from Config.config import DB_SENDER_HOST, DB_SENDER_USER, DB_SENDER_PASSWORD, DB_SENDER_NAME
from DataBase.MySql import MySql
from FloorSetterAbstract import FloorSetterAbstract
from Exceptions.Exceptions import CannotGetToken, WrongToken
import requests


class YandexFloorChanger(FloorSetterAbstract):

    def __init__(self, floor_id, floor_multiplier, new_coefficient, regions_with_prices):
        self.floor_id = floor_id
        self.floor_multiplier = float(floor_multiplier)
        self.geo = regions_with_prices
        self.new_coefficient = float(new_coefficient)
        self.url = 'https://partner.yandex.ru/restapi/v1/mobile_app_rtb/'
        self.cookie = self.get_header(MySql(host=DB_SENDER_HOST,
                                            user=DB_SENDER_USER,
                                            password=DB_SENDER_PASSWORD,
                                            db=DB_SENDER_NAME).get_headers(
            ad_service='Yandex',
            header_name='Cookie'))
        self.headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json',
        }
        self.headers.update(self.cookie)
        self.headers.update(self.get_token())

    @staticmethod
    def get_header(rows) -> dict:
        headers = {}
        for row in rows:
            headers.update(
                {row.get('HeaderName'): row.get('HeaderValue')}
            )
        return headers

    def get_token(self):
        req = requests.get(
            url='https://partner.yandex.ru/restapi/v1/resources',
            headers=self.headers
        )

        match req.status_code:
            case 200:
                answer = {'X-Frontend-Authorization': req.headers['X-Frontend-Authorization']}
            case _:
                raise CannotGetToken

        return answer

    def change_price(self):
        url = self.url + self.floor_id
        headers = self.headers
        data = {"data": {
            "attributes": {"geo": f"{self.geo}",
                           "mincpm": f"{self.floor_multiplier * self.new_coefficient:.2f}"},
            "type": "mobile_app_rtb",
            "id": self.floor_id}}

        req = requests.patch(
            url=url,
            headers=headers,
            json=data
        )

        match req.status_code:
            case 401:
                raise WrongToken
            case 200:
                return True
            case _:
                print(req.status_code)
                print(req.text)
                raise Exception


YandexFloorChanger(
    floor_id='R-M-2065104-11',
    regions_with_prices='[{\"id\":\"187\",\"cpm\":0.212321},'
                        '{\"id\":\"225\",\"cpm\":1.2},'
                        '{\"id\":\"111\",\"cpm\":231}]',
    floor_multiplier='2',
    new_coefficient='7.231'
).change_price()
