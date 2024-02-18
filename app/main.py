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


def parse_date_interval(interval_type, date_interval) -> relativedelta:
    if interval_type == "months":
        date_interval = relativedelta(months=date_interval)
    elif interval_type == "weeks":
        date_interval = relativedelta(weeks=date_interval)
    return date_interval


def main(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    download = config.get("download")
    if download.get("enabled"):
        logger.info("Downloading images...")
        start_date = datetime.strptime(download.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(download.get("end_date"), "%Y-%m-%d")
        logger.info("Dates: {} - {}".format(start_date, end_date))
        interval_type = download.get("interval_type", "weeks")
        date_interval = download.get("date_interval", 1)
        download(
            config["bbox"],
            config["evalscript"],
            start_date,
            end_date,
            parse_date_interval(interval_type, date_interval),
            config["name_id"],
        )

    train = config.get("train")
    if train.get("enabled"):
        logger.info("Training models...")
        start_date = datetime.strptime(train.get("start_date"), "%Y-%m-%d")
        interval_type = train.get("interval_type", "weeks")
        date_interval = train.get("date_interval", 1)
        process_data = ProcessData(
            config["name_id"],
            parse_date_interval(interval_type, date_interval),
            start_date,
            config["bands"],
            config["formula"],
        )
        df = process_data.create_dataframe(train.get("kpi"))
        logger.info("Dataframe: \n{}".format(df))
        models = []
        for model in config["models"]:
            if model == "arima":
                models.append(ArimaModel(df, train.get("kpi")))
            elif model == "random_forest":
                models.append(RandomForestModel(df, train.get("kpi")))
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
