
class VunglePlacements:
    def __init__(self):
        self.i = {
            'i.bid': 'i.bid.',
            # 'i.00.60': 'i.00.60.',
            # 'i.01.25': 'i.01.25.',
            # 'i.02.50': 'i.02.50.',
            # 'i.05.00': 'i.05.00.',
            # 'i.09.00': 'i.09.00.',
            # 'i.16.00': 'i.16.00.',
            # 'i.25.00': 'i.25.00.',
            # 'i.30.00': 'i.30.00.',
        }
        self.b = {
            'b.bid': 'b.bid.',
            # 'b.00.15': 'b.00.15.',
        }
        self.v = {
            'v.bid': 'v.bid.',
            # 'v.00.60': 'v.00.60.',
            # 'v.01.25': 'v.01.25.',
            # 'v.02.50': 'v.02.50.',
            # 'v.05.00': 'v.05.00.',
            # 'v.09.00': 'v.09.00.',
            # 'v.16.00': 'v.16.00.',
            # 'v.25.00': 'v.25.00.',
            # 'v.30.00': 'v.30.00.',
        }

    def get_interstitial(self):
        return self.i.copy()

    def get_banner(self):
        return self.b.copy()

    def get_rewarded(self):
        return self.v.copy()

    def get_all(self):
        return {**self.b.copy(), **self.v.copy(), **self.i.copy()}
