import logging

from dotenv import load_dotenv

from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class Model:

    def __init__(self, df, kpi):
        self.df = df
        self.kpi = kpi

    def train_model(self) -> None: ...

    def predict(self) -> None: ...

    def evaluate(self) -> None: ...

    def visualize(self) -> None: ...

    def save_model(self) -> None: ...

    def load_model(self) -> None: ...
