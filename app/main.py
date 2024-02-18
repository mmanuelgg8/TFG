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

    name_id = config.get("name_id")
    download_config = config.get("download")
    if download_config.get("enabled"):
        logger.info("Downloading images...")
        start_date = datetime.strptime(download_config.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(download_config.get("end_date"), "%Y-%m-%d")
        logger.info("Dates: {} - {}".format(start_date, end_date))
        interval_type = download_config.get("interval_type", "weeks")
        date_interval = download_config.get("date_interval", 1)
        download(
            bbox=download_config.get("bbox"),
            evalscript=download_config.get("evalscript"),
            start_date=start_date,
            end_date=end_date,
            date_interval=parse_date_interval(interval_type, date_interval),
            name_id=name_id,
        )

    train_config = config.get("train")
    if train_config.get("enabled"):
        logger.info("Training models...")
        start_date = datetime.strptime(train_config.get("start_date"), "%Y-%m-%d")
        interval_type = train_config.get("interval_type", "weeks")
        date_interval = train_config.get("date_interval", 1)
        process_data = ProcessData(
            name_id=name_id,
            date_interval=parse_date_interval(interval_type, date_interval),
            start_date=start_date,
            band_names=config.get("bands"),
            formula=train_config.get("formula"),
        )
        df = process_data.create_dataframe(train_config.get("kpi"))
        logger.info("Dataframe: \n{}".format(df))
        models = []
        for model in train_config.get("models"):
            if model == "arima":
                models.append(ArimaModel(df, train_config.get("kpi")))
            elif model == "random_forest":
                models.append(RandomForestModel(df, train_config.get("kpi")))
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
