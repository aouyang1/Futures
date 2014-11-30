__author__ = 'aouyang1'

import pandas as pd


class CurrentHLOC:

    def __init__(self):
        self.High = 0
        self.Low = 0
        self.Open = 0
        self.Close = 0
        self.Volume = 0
        self.CloseTime = pd.Timestamp('01-01-1960 00:00:00')