__author__ = 'aouyang1'


class DailyTick:

    def __init__(self):
        self.df = None
        self.date = []
        self.last = []
        self.volume = []
        self.cnt = 0

    def curr_last(self):
        return self.last[self.cnt]

    def curr_vol(self):
        return self.volume[self.cnt]

    def curr_date(self):
        return self.date[self.cnt]

    def prev_last(self):
        if self.cnt == 0:
            return 0.0
        else:
            return self.last[self.cnt-1]

    def prev_vol(self):
        if self.cnt == 0:
            return 0.0
        else:
            return self.last[self.cnt-1]

    def prev_date(self):
        if self.cnt == 0:
            return '1960-01-01'
        else:
            return self.date[self.cnt-1]

    def set_lists(self):
        self.date = self.df.index
        self.last = self.df['Last'].tolist()
        self.volume = self.df['Volume'].tolist()




