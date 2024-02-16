import argparse
import json
import logging
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from models.arima import ArimaModel
from models.random_forest import RandomForestModel
from scripts.download import download
from utils import set_logging
from utils.process_data import ProcessData

set_logging()
logger = logging.getLogger(__name__)


def main(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
    interval_type = config.get("interval_type", "weeks")
    date_interval = config.get("date_interval", 1)

    if interval_type == "months":
        date_interval = relativedelta(months=date_interval)
    elif interval_type == "weeks":
        date_interval = relativedelta(weeks=date_interval)

    if config.get("download"):
        logger.info("Downloading images...")
        logger.info("Dates: {} - {}".format(start_date, end_date))
        download(
            config["bbox"],
            config["evalscript"],
            start_date,
            end_date,
            date_interval,
            config["name_id"],
        )

    if config.get("train"):
        logger.info("Training models...")
        process_data = ProcessData(config["name_id"], date_interval, start_date, config["bands"], config["formula"])
        df = process_data.create_dataframe(config["kpi"])
        logger.info("Dataframe: \n{}".format(df))
        models = []
        for model in config["models"]:
            if model == "arima":
                models.append(ArimaModel(df, config["kpi"]))
            elif model == "random_forest":
                models.append(RandomForestModel(df, config["kpi"]))
        for model in models:
            model.train_model()
            model.evaluate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and train models")
    parser.add_argument("--config_file", "-c", type=str, help="Name of the JSON configuration file")
    args = parser.parse_args()
    logger.info("Using config file: " + args.config_file)
    path = os.path.join(os.path.dirname(__file__), "..", "resources", "properties", args.config_file)
    main(path)
