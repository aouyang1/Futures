from pandas import Series


class DailyTick:

    def __init__(self):
        self.df = None
        self.cnt = 0

    def get_curr_tick(self):
        return self.df.ix[self.cnt]

    def get_prev_tick(self):
        if self.cnt == 0:
            return Series({'Last': 0.0, 'Volume': 0}, name='1960-01-01')
        else:
            return self.df.ix[self.cnt - 1]




