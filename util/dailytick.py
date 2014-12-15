__author__ = 'aouyang1'


class DailyTick:

    def __init__(self):
        self.df = None
        self.date = []
        self.last = []
        self.volume = []
        self.cnt = 0

    def get_curr_tick(self):
        return {'Last': self.last[self.cnt],
                'Volume': self.volume[self.cnt],
                'Date': self.date[self.cnt]}

    def get_prev_tick(self):
        if self.cnt == 0:
            return {'Last': 0.0,
                    'Volume': 0,
                    'Date': '1960-01-01'}
        else:
            return {'Last': self.last[self.cnt-1],
                    'Volume': self.volume[self.cnt-1],
                    'Date': self.date[self.cnt-1]}

    def set_lists(self):
        self.date = self.df.index
        self.last = self.df['Last']
        self.volume = self.df['Volume']




