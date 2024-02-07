import numpy as np


class KPIs:
    def __init__(self, data, axis):
        self.data = data
        self.axis = axis

    def get_mean(self):
        return np.mean(self.data, axis=self.axis)

    def get_max(self):
        return np.max(self.data, axis=self.axis)

    def get_min(self):
        return np.min(self.data, axis=self.axis)

    def get_std(self):
        return np.std(self.data, axis=self.axis)
