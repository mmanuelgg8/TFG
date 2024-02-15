import argparse
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from utils.process_data import ProcessData
from models.arima import ArimaModel
from models.random_forest import RandomForestModel
from scripts.download import download
from utils import set_logging

set_logging()
logger = logging.getLogger(__name__)


def main():
    available_models = ["arima", "random_forest"]
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
    parser.add_argument("--models", choices=available_models, nargs="+", help="Models to train")
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
        process_data = ProcessData(args.name_id, args.date_interval, args.start_date, args.bands, args.formula)
        df = process_data.create_dataframe(args.kpi)
        logger.info("Dataframe: \n{}".format(df))
        models = []
        for model in args.models:
            if model == "arima":
                models.append(ArimaModel(df, args.kpi))
            elif model == "random_forest":
                models.append(RandomForestModel(df, args.kpi))
        for model in models:
            model.train_model()
            model.evaluate()


if __name__ == "__main__":
    main()
