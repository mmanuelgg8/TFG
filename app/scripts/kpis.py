from enum import Enum

import numpy as np


class KPIsConstants(Enum):
    MEAN = "mean"
    MAX = "max"
    MIN = "min"
    STD = "std"


def parse_to_constant_kpi(kpi: str) -> KPIsConstants:
    try:
        return KPIsConstants(kpi)
    except ValueError:
        return KPIsConstants.MEAN


class KPIs:
    def __init__(self, data, axis, kpi: KPIsConstants):
        self.data = data
        self.axis = axis
        self.kpi = kpi

    def get_kpi(self):
        if self.kpi == KPIsConstants.MEAN:
            return self.get_mean()
        elif self.kpi == KPIsConstants.MAX:
            return self.get_max()
        elif self.kpi == KPIsConstants.MIN:
            return self.get_min()
        elif self.kpi == KPIsConstants.STD:
            return self.get_std()

    def get_mean(self):
        return np.mean(self.data, axis=self.axis)

    def get_max(self):
        return np.max(self.data, axis=self.axis)

    def get_min(self):
        return np.min(self.data, axis=self.axis)

    def get_std(self):
        return np.std(self.data, axis=self.axis)
