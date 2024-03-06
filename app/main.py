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
from configuration.configuration import Configuration

set_logging()
logger = logging.getLogger(__name__)


def parse_date_interval(interval_type, date_interval) -> relativedelta:
    if interval_type == "months":
        date_interval = relativedelta(months=date_interval)
    elif interval_type == "weeks":
        date_interval = relativedelta(weeks=date_interval)
    return date_interval


def main(config_file):
    configuration = Configuration()
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
    if (
        train_config.get("enabled")
        or train_config.get("save_model")
        or train_config.get("save_visualization")
        or train_config.get("predict")
    ):
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
        for model_name in train_config.get("models"):
            if model_name == "arima":
                models.append(ArimaModel(df, train_config.get("kpi")))
            elif model_name == "random_forest":
                models.append(RandomForestModel(df, train_config.get("kpi")))
        if train_config.get("enabled"):
            for model in models:
                model.train_model()
                model.evaluate()
            if train_config.get("save_model"):
                models_path = str(configuration["models_path"])
                if not os.path.exists(models_path):
                    os.makedirs(models_path)
                    logger.info(f"Directory {models_path} created")
                model_path = os.path.join(models_path, f"{name_id}_{model.__class__.__name__}.sav")
                model.save_model(model_path)
        if train_config.get("load_model"):
            models_path = str(configuration["models_path"])
            if not os.path.exists(models_path):
                raise FileNotFoundError(f"Directory {models_path} not found")
            for model in models:
                model_path = os.path.join(models_path, f"{name_id}_{model.__class__.__name__}.sav")
                model.model_fit = model.load_model(model_path)
        if train_config.get("predict"):
            for model in models:
                model.predict(train_config.get("model_name"))
        if train_config.get("save_visualization"):
            visualizations_path = str(configuration["visualizations_path"])
            if not os.path.exists(visualizations_path):
                os.makedirs(visualizations_path)
                logger.info(f"Directory {visualizations_path} created")
            for model in models:
                visualization_path = os.path.join(visualizations_path, f"{name_id}_{model.__class__.__name__}.png")
                if os.path.exists(visualization_path):
                    os.remove(visualization_path)
                    logger.info(f"File {visualization_path} removed")
                model.save_visualization(visualization_path, train_config.get("interval_type"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and train models")
    parser.add_argument("--config_file", "-c", type=str, help="Name of the JSON configuration file")
    args = parser.parse_args()
    logger.info("Using config file: " + args.config_file)
    path = os.path.join(os.path.dirname(__file__), "..", "resources", "properties", args.config_file)
    main(path)
