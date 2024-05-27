
class YandexPlacements:
    def __init__(self):
        self.i = {
            'Interstitial Default': 'i.Def.',
            'Interstitial 00.70': 'i.00.70.',
            'Interstitial 01.00': 'i.01.00.',
            'Interstitial 01.50': 'i.01.50.',
            'Interstitial 02.00': 'i.02.00.',
            'Interstitial 02.50': 'i.02.50.',
            'Interstitial 03.00': 'i.03.00.',
            'Interstitial 03.50': 'i.03.50.',
            'Interstitial 04.00': 'i.04.00.',
            'Interstitial 05.00': 'i.05.00.',
            'Interstitial 06.00': 'i.06.00.',
            'Interstitial 07.00': 'i.07.00.',
        }
        self.b = {
            'Banner Default': 'b.Def.',
            'Banner 00.10': 'b.00.10.',
            'Banner 00.20': 'b.00.20.',
            'Banner 00.25': 'b.00.25.',
            'Banner 00.30': 'b.00.30.',
            'Banner 00.40': 'b.00.40.',
            'Banner 00.50': 'b.00.50.',
        }
        self.v = {
            'Rewarded Default': 'v.Def.',
            'Rewarded 00.70': 'v.00.70.',
            'Rewarded 01.00': 'v.01.00.',
            'Rewarded 01.50': 'v.01.50.',
            'Rewarded 02.00': 'v.02.00.',
            'Rewarded 02.50': 'v.02.50.',
            'Rewarded 03.00': 'v.03.00.',
            'Rewarded 03.50': 'v.03.50.',
            'Rewarded 04.00': 'v.04.00.',
            'Rewarded 05.00': 'v.05.00.',
            'Rewarded 06.00': 'v.06.00.',
            'Rewarded 07.00': 'v.07.00.',
        }

    def get_interstitial(self):
        return self.i.copy()

    def get_banner(self):
        return self.b.copy()

    def get_rewarded(self):
        return self.v.copy()

    def get_all(self):
        return {**self.b.copy(), **self.v.copy(), **self.i.copy()}
