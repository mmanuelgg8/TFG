import logging
import pickle

import joblib
from dotenv import load_dotenv
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class Model:

    def __init__(self, df, kpi):
        self.df = df
        self.kpi = kpi
        self.model_fit = None

    def train_model(self) -> None: ...

    def predict(self) -> None: ...

    def evaluate(self) -> None: ...

    def visualize(self) -> None: ...

    def save_model(self, model_name: str) -> None:
        if not model_name.endswith(".sav"):
            raise RuntimeError("Filename should end with '.sav'")
        # pickle.dump(self.model_fit, open(model_name, "wb"))
        joblib.dump(self.model_fit, model_name)

    def load_model(self, model_name: str) -> ARIMAResults:
        # return pickle.load(open(model_name, "rb"))
        return joblib.load(model_name)
