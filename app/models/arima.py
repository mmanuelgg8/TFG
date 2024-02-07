from datetime import datetime
import logging
from typing import List
from matplotlib.dates import relativedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from models.forecast import Model
from scripts.kpis import KPIs
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(Model):
    def __init__(self, geotiffs_paths: str, date_interval: relativedelta, start_date: datetime):
        super().__init__(geotiffs_paths, date_interval, start_date)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        self.preprocess_data()
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        self.model = ARIMA(self.train["mean"], order=(5, 1, 0))
        self.model_fit = self.model.fit()

        logger.info("Training complete.")

    def evaluate(self):
        self.predictions = self.model_fit.forecast(steps=len(self.test))
        self.errors = mean_squared_error(self.test["mean"], self.predictions)

        logger.info("Mean Squared Error: {}".format(self.errors))
