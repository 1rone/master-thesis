import pymysql
from pymysql.cursors import DictCursor
from pymysql.constants import CLIENT


class DataBase:

    def __init__(self, host, user, password, db, port=None):
        if port:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                port=port,
                password=password,
                db=db,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True,
                client_flag=CLIENT.MULTI_STATEMENTS
            )
        else:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True,
                client_flag=CLIENT.MULTI_STATEMENTS
            )

    def close_connection(self):
        self.connection.close()

    def open_connection(self, host, user, password, db, port=None):
        if port:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                port=port,
                password=password,
                db=db,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True,
                client_flag=CLIENT.MULTI_STATEMENTS
            )
        else:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True,
                client_flag=CLIENT.MULTI_STATEMENTS
            )
