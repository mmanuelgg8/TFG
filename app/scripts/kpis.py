from enum import Enum
from typing import Optional, Tuple

import numpy as np
from numpy.core.multiarray import ndarray


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
    def __init__(self, data: ndarray, axis: Tuple, kpi: KPIsConstants):
        self.data: ndarray = data
        self.axis: Tuple = axis
        self.kpi: KPIsConstants = kpi

    def get_kpi(self) -> Optional[ndarray]:
        if self.kpi == KPIsConstants.MEAN:
            return self.get_mean()
        elif self.kpi == KPIsConstants.MAX:
            return self.get_max()
        elif self.kpi == KPIsConstants.MIN:
            return self.get_min()
        elif self.kpi == KPIsConstants.STD:
            return self.get_std()

    def get_mean(self) -> ndarray:
        return np.mean(self.data, axis=self.axis)

    def get_max(self) -> ndarray:
        return np.max(self.data, axis=self.axis)

    def get_min(self) -> ndarray:
        return np.min(self.data, axis=self.axis)

    def get_std(self) -> ndarray:
        return np.std(self.data, axis=self.axis)
