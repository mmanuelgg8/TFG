import logging

# import pickle
from typing import Any

import joblib
from dotenv import load_dotenv
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

    def predict(self, model_name: str) -> None: ...

    def evaluate(self) -> None: ...

    def visualize(self) -> None: ...

    def save_visualization(self, path: str, name_id: str, interval_type: str) -> None: ...

    def save_model(self, model_name: str) -> None:
        if not model_name.endswith(".sav"):
            raise RuntimeError("Filename should end with '.sav'")
        # pickle.dump(self.model_fit, open(model_name, "wb"))
        self.model_name = model_name
        joblib.dump(self.model_fit, model_name)
        logger.info(f"Model saved as {model_name}")

    def load_model(self, model_name: str) -> Any:
        # return pickle.load(open(model_name, "rb"))
        if not model_name.endswith(".sav"):
            raise RuntimeError("Filename should end with '.sav'")
        if model_name is None:
            if self.model_name is None:
                raise RuntimeError("Model name not found")
            model_name = self.model_name

        logger.info(f"Loading model {model_name}")
        return joblib.load(model_name)
