import argparse
import json
import logging
import os
import shutil
from datetime import datetime
from importlib import import_module

import numpy as np
from configuration.configuration import Configuration
from dateutil.relativedelta import relativedelta
from numpy.core.multiarray import ndarray
from pandas import DataFrame
from rasterio import rasterio
from scripts.download import download
from utils import set_logging
from utils.process_data import create_dataframe, tifs_to_array

set_logging()
logger = logging.getLogger(__name__)


def parse_date_interval(interval_type, date_interval) -> relativedelta:
    if interval_type == "months":
        date_interval = relativedelta(months=date_interval)
    elif interval_type == "weeks":
        date_interval = relativedelta(weeks=date_interval)
    return date_interval


def init_models(model_names: str, df: DataFrame, kpi: slice, model_params: dict):
    models = []
    for model_name in model_names:
        try:
            module_name = "".join([word.capitalize() for word in model_name.split("_")])
            module = import_module(f"models.{model_name}")
            model = getattr(module, f"{module_name}Model")
            models.append(model(df, kpi, model_params.get(model_name)))
        except (AttributeError, ImportError):
            logger.error(f"Model {model_name} not found")
    return models


def main(config_file):
    configuration = Configuration()
    GEOTIFFS_PATH: str = str(configuration["geotiffs_path"])
    with open(config_file, "r") as f:
        config = json.load(f)

    interval_type = config.get("interval_type", "weeks")
    date_interval = config.get("date_interval", 1)
    parsed_date_interval = parse_date_interval(interval_type, date_interval)
    name_id = config.get("name_id")
    download_config = config.get("download")
    if download_config.get("enabled"):
        if download_config.get("remove_previous_download"):
            shutil.rmtree(GEOTIFFS_PATH + config.get("name_id"))
            logger.info("Previous download removed")
        logger.info("Downloading images...")
        start_date = datetime.strptime(download_config.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(download_config.get("end_date"), "%Y-%m-%d")
        logger.info("Dates: {} - {}".format(start_date, end_date))
        download(
            bbox=download_config.get("bbox"),
            evalscript=download_config.get("evalscript"),
            start_date=start_date,
            end_date=end_date,
            date_interval=parsed_date_interval,
            name_id=name_id,
            format=download_config.get("format"),
            url=download_config.get("url"),
            satellite_type=download_config.get("satellite_type"),
            data_filter=download_config.get("data_filter"),
            token_url=download_config.get("token_url"),
            client_id_env=download_config.get("client_id_env"),
            client_secret_env=download_config.get("client_secret_env"),
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
        tiffs, time_values = tifs_to_array(
            name_id, start_date, parsed_date_interval, interval_type
        )
        data = []
        for tif in tiffs:
            with rasterio.open(tif) as src:
                data.append(src.read())

        data = np.array(data)  # (image, bands, height, width)
        data = data.reshape(
            data.shape[0], data.shape[2], data.shape[3]
        )  # (image, height, width)
        logger.info("Data shape: {}".format(data[:, 0, 0]))
        normalized_data: ndarray = np.nan_to_num(data, nan=0, posinf=0, neginf=0) / 255
        df = create_dataframe(normalized_data, time_values, train_config.get("kpi"))
        logger.info("Dataframe: \n{}".format(df))
        model_params = train_config.get("model_params")
        models = init_models(
            train_config.get("models"), df, train_config.get("kpi"), model_params
        )
        if train_config.get("enabled"):
            for model in models:
                model.train_model()
                model.evaluate()
                if train_config.get("save_model"):
                    models_path = str(configuration["models_path"])
                    if not os.path.exists(models_path):
                        os.makedirs(models_path)
                        logger.info(f"Directory {models_path} created")
                    model_path = os.path.join(
                        models_path, f"{name_id}_{model.__class__.__name__}.sav"
                    )
                    model.save_model(model_path)
        if train_config.get("load_model"):
            models_path = str(configuration["models_path"])
            if not os.path.exists(models_path):
                raise FileNotFoundError(f"Directory {models_path} not found")
            for model in models:
                model_path = os.path.join(
                    models_path, f"{name_id}_{model.__class__.__name__}.sav"
                )
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
                visualization_path = os.path.join(
                    visualizations_path, f"{name_id}_{model.__class__.__name__}.png"
                )
                if os.path.exists(visualization_path):
                    os.remove(visualization_path)
                    logger.info(f"File {visualization_path} removed")
                model.save_visualization(
                    visualization_path, name_id, config.get("interval_type")
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and train models")
    parser.add_argument(
        "--config_file", "-c", type=str, help="Name of the JSON configuration file"
    )
    args = parser.parse_args()
    logger.info("Using config file: " + args.config_file)
    path = os.path.join(
        os.path.dirname(__file__), "..", "resources", "properties", args.config_file
    )
    main(path)
