class Placements:
    def __init__(self):
        self.i = {}
        self.v = {}
        self.b = {}

    def get_interstitial(self):
        return self.i.copy()

    def get_rewarded(self):
        return self.v.copy()

    def get_banner(self):
        return self.b.copy()

    def get_all(self):
        return {self.get_banner(), self.get_rewarded(), self.get_interstitial()}
