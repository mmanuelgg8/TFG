import logging
from typing import Dict, List

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from models.ml_model import Model
from pandas import DataFrame
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class RandomForestModel(Model):
    def __init__(self, df: DataFrame, kpi: slice, model_params: Dict = {}):
        super().__init__(df, kpi)
        self.model_params: Dict = model_params

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        self.train: List = self.train
        self.test: List = self.test
        n_estimators = self.model_params.get("n_estimators", 100)
        max_depth = self.model_params.get("max_depth", None)
        model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
        self.model_fit: RandomForestRegressor = model.fit(
            self.train, self.train[self.kpi]
        )

        logger.info("Training complete.")

    def evaluate(self) -> None:
        predictions = self.model_fit.predict(self.test)
        errors = mean_squared_error(self.test[self.kpi], predictions)
        score = self.model_fit.score(self.test, predictions)

        logger.info("Score: {}".format(score))
        logger.info("Mean Squared Error: {}".format(errors))

    def predict(self, model_name: str) -> None:
        if self.model_fit is None:
            try:
                if self.model_name:
                    self.model_fit = self.load_model(self.model_name)
                if model_name:
                    self.model_fit = self.load_model(model_name)
            except Exception as e:
                logger.error("Error loading model")
                raise e
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        predictions = self.model_fit.predict(self.test)
        logger.info("Predictions: {}".format(predictions))

    def save_visualization(self, path: str, name_id: str, interval_type: str) -> None:
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        plt.plot(self.train[self.kpi], color="blue")
        plt.plot(self.test[self.kpi], color="orange")
        prediction = self.model_fit.predict(self.test)
        plt.plot(
            range(len(self.train), len(self.train) + len(self.test)),
            prediction,
            color="green",
        )
        future = self.model_fit.predict(self.df)
        plt.plot(
            range(len(self.df), len(self.df) + len(future)), future, color="purple"
        )
        plt.legend(["Training", "Test", "Prediction", "Future"])
        plt.title(f"{name_id} - Random Forest Model")
        plt.xlabel(f"Time ({interval_type})")
        plt.ylabel(f"KPI ({self.kpi})")
        plt.savefig(path)
        plt.close()
        logger.info(f"Visualization saved as {path}")
