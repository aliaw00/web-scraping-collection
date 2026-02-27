import json
import logging
import random
import time
import requests

from database import init_db, save_price
from scraper import get_price
from notifier import send_alert
from config import CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX, LOG_FILE

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    return parser.parse_args()

def load_products():
    with open("products.json", "r") as f:
        return json.load(f)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def run_once():
    products = load_products()
    session = requests.Session()

    for product in products:
        price = get_price(session, product["url"])
        save_price(product["name"], product["url"], price)

        if price:
            logging.info(f"{product['name']} → {price}")

            if price <= product["target_price"]:
                send_alert(product["name"], price)
        else:
            logging.info(f"can't find price!!!")


if __name__ == "__main__":
    setup_logging()
    init_db()

    args = parse_args()

    if args.loop:
        while True:
            run_once()
            sleep_time = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
            logging.info(f"Sleeping {sleep_time}s")
            time.sleep(0.1)
    else:
        run_once()
