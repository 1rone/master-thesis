from abc import ABC, abstractmethod


class FloorSetterAbstract(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def change_price(self):
        pass
