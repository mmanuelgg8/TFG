import logging
import argparse
from datetime import datetime

from dateutil.relativedelta import relativedelta
from models.arima import ArimaModel
from models.random_forest import RandomForestModel
from scripts.download import download
from utils import set_logging

set_logging()
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Download and train models")
    parser.add_argument("--bbox", type=float, nargs=4, help="Bounding box coordinates")
    parser.add_argument("--evalscript", type=str, help="Evalscript")
    parser.add_argument("--start_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), help="Start date")
    parser.add_argument("--end_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), help="End date")
    parser.add_argument("--date_interval", type=int, help="Date interval")
    parser.add_argument("--interval_type", choices=["months", "weeks"], default="weeks", help="Interval type")
    parser.add_argument("--name_id", type=str, help="Name id")
    parser.add_argument("--bands", type=str, nargs="+", help="Bands")
    parser.add_argument("--formula", type=str, help="Formula")
    parser.add_argument("--kpi", choices=["mean", "max", "min", "std"], default="mean", help="KPI")
    parser.add_argument("--download", action="store_true", help="Download")
    parser.add_argument("--train", action="store_true", help="Train")
    args = parser.parse_args()

    if args.interval_type == "months":
        args.date_interval = relativedelta(months=args.date_interval)
    elif args.interval_type == "weeks":
        args.date_interval = relativedelta(weeks=args.date_interval)

    if args.download:
        logger.info("Downloading images...")
        download(args.bbox, args.evalscript, args.start_date, args.end_date, args.date_interval, args.name_id)

    if args.train:
        logger.info("Training models...")
        arima = ArimaModel(args.date_interval, args.start_date, args.bands, args.formula, args.kpi)
        random_forest = RandomForestModel(args.date_interval, args.start_date, args.bands, args.formula, args.kpi)
        arima.train_model()
        random_forest.train_model()
        arima.evaluate()
        random_forest.evaluate()


if __name__ == "__main__":
    main()
    # Isla Mayor, Sevilla
    # bands = ["B04", "B08"]
    # logger.info("Bands: {}".format(bands))
    # formula = "NDVI"
    # min_x, min_y = -6.215864855019264, 37.162534357525814
    # max_x, max_y = -6.111682075391747, 37.10259292740977
    # bbox = [min_x, min_y, max_x, max_y]
    # evalscript = "ndvi"
    # start_date = datetime(2017, 1, 1)
    # # start_date = datetime(2021, 1, 1)
    # end_date = datetime(2022, 1, 1)
    # date_interval = relativedelta(weeks=1)
    # name_id = "islamayor_ndvi_"
    # # logger.info("Downloading images...")
    # download(bbox, evalscript, start_date, end_date, date_interval, name_id)

    # logger.info("Training models...")
    # arima = ArimaModel(date_interval, start_date, bands, formula)
    # random_forest = RandomForestModel(date_interval, start_date, bands, formula)
    #
    # arima.train_model()
    # random_forest.train_model()
    #
    # arima.evaluate()
    # random_forest.evaluate()
