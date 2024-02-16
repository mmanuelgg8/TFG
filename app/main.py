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
    path = os.path.join(os.path.dirname(__file__), "../resources/properties/" + args.config_file)
    main(path)

# def main():
#     available_models = ["arima", "random_forest"]
#     parser = argparse.ArgumentParser(description="Download and train models")
#     parser.add_argument("--bbox", type=float, nargs=4, help="Bounding box coordinates")
#     parser.add_argument("--evalscript", type=str, help="Evalscript")
#     parser.add_argument("--start_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), help="Start date")
#     parser.add_argument("--end_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), help="End date")
#     parser.add_argument("--date_interval", type=int, help="Date interval")
#     parser.add_argument("--interval_type", choices=["months", "weeks"], default="weeks", help="Interval type")
#     parser.add_argument("--name_id", type=str, help="Name id")
#     parser.add_argument("--bands", type=str, nargs="+", help="Bands")
#     parser.add_argument("--formula", type=str, help="Formula")
#     parser.add_argument("--kpi", choices=["mean", "max", "min", "std"], default="mean", help="KPI")
#     parser.add_argument("--download", action="store_true", help="Download")
#     parser.add_argument("--train", action="store_true", help="Train")
#     parser.add_argument("--models", choices=available_models, nargs="+", help="Models to train")
#     args = parser.parse_args()
#
#     if args.interval_type == "months":
#         args.date_interval = relativedelta(months=args.date_interval)
#     elif args.interval_type == "weeks":
#         args.date_interval = relativedelta(weeks=args.date_interval)
#
#     if args.download:
#         logger.info("Downloading images...")
#         download(args.bbox, args.evalscript, args.start_date, args.end_date, args.date_interval, args.name_id)
#
#     if args.train:
#         logger.info("Training models...")
#         process_data = ProcessData(args.name_id, args.date_interval, args.start_date, args.bands, args.formula)
#         df = process_data.create_dataframe(args.kpi)
#         logger.info("Dataframe: \n{}".format(df))
#         models = []
#         for model in args.models:
#             if model == "arima":
#                 models.append(ArimaModel(df, args.kpi))
#             elif model == "random_forest":
#                 models.append(RandomForestModel(df, args.kpi))
#         for model in models:
#             model.train_model()
#             model.evaluate()
#
#
# if __name__ == "__main__":
#     main()
