from abc import ABC, abstractmethod


class AdServiceAbstract(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_app(self):
        pass

    @abstractmethod
    def auto_writing(self):
        pass
