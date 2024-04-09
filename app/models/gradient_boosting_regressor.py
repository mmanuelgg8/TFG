import logging

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from models.ml_model import Model
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class GradientBoostingRegressorModel(Model):
    def __init__(self, df, kpi, model_params):
        super().__init__(df, kpi)
        if model_params is None:
            model_params = {}
        self.model_params = model_params

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        self.train: list = self.train
        # logger.info("Train: \n{}".format(self.train))
        # logger.info("Test: \n{}".format(self.test))
        n_estimators = self.model_params.get("n_estimators", 100)
        max_depth = self.model_params.get("max_depth", None)
        model = GradientBoostingRegressor(n_estimators=n_estimators, max_depth=max_depth)
        self.model_fit = model.fit(self.train, self.train[self.kpi])

        logger.info("Training complete.")

    def evaluate(self):
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
        predictions = self.model_fit.apply(self.test)
        logger.info("Predictions: {}".format(predictions))

    def save_visualization(self, path: str, name_id: str, interval_type: str) -> None:
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        plt.plot(self.train[self.kpi], color="blue")
        plt.plot(self.test[self.kpi], color="orange")
        predictions = self.model_fit.apply(self.test)
        off_set = len(self.train)
        plt.plot(range(off_set, off_set + len(predictions)), predictions, color="green")
        plt.legend(["Train", "Test", "Predictions"])
        plt.title(f"{name_id} - Gradient Boosting Regressor Model")
        plt.xlabel(f"Time ({interval_type})")
        plt.ylabel(f"KPI ({self.kpi})")
        plt.savefig(path)
        plt.close()
        logger.info(f"Visualization saved as {path}")
