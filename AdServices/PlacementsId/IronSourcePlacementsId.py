class IronSourcePlacements:
    def __init__(self):
        self.i = {
            'i.def': 'i.def.',
            'i.x0.70': 'i.x0.70.',
            'i.x1.10': 'i.x1.10.',
            'i.x1.35': 'i.x1.35.',
            'i.x1.55': 'i.x1.55.',
            'i.x1.90': 'i.x1.90.',
            'i.x2.10': 'i.x2.10.',
            'i.x2.50': 'i.x2.50.',
        }

        self.v = {
            'v.def': 'v.def.',
            'v.x0.70': 'v.x0.70.',
            'v.x1.10': 'v.x1.10.',
            'v.x1.35': 'v.x1.35.',
            'v.x1.55': 'v.x1.55.',
            'v.x1.90': 'v.x1.90.',
            'v.x2.10': 'v.x2.10.',
            'v.x2.50': 'v.x2.50.',
        }

    def get_interstitial(self):
        return self.i.copy()

    def get_rewarded(self):
        return self.v.copy()

    def get_all(self):
        return {**self.v.copy(), **self.i.copy()}
