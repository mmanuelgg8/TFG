from datetime import datetime
import logging
from matplotlib.dates import relativedelta

from dotenv import load_dotenv
from models.ml_model import Model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class RandomForestModel(Model):
    def __init__(self, geotiffs_path: str, date_interval: relativedelta, start_date: datetime):
        super().__init__(geotiffs_path, date_interval, start_date)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))
        # Train the model on the mean over time
        self.preprocess_data()
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        logger.info("Train: \n{}".format(self.train))
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(self.train, self.train["mean"])

        logger.info("Training complete.")

    def evaluate(self):
        self.predictions = self.model.predict(self.test)
        self.errors = mean_squared_error(self.test["mean"], self.predictions)

        logger.info("Mean Squared Error: {}".format(self.errors))
