class UnityBlockedCategories:
    def __init__(self):
        self._always = ['card', 'casino', 'alcoholicBeverages',
                        'lotteryGambling', 'religionSpirituality', 'datingSocialMedia', 'dice',
                        'lawGovernmentPolitics', 'realMoneyGambling']
        self._toddlers = self._always.copy() + ['personalFinance']
        self._kids = self._always.copy() + ['personalFinance']
        self._teens = self._always.copy()
        self._mature = self._always.copy()
        self._adults = []

    def get_toddlers(self):
        return self._toddlers.copy()

    def get_kids(self):
        return self._kids.copy()

    def get_teens(self):
        return self._teens.copy()

    def get_mature(self):
        return self._mature.copy()

    def get_adults(self):
        return self._adults.copy()

