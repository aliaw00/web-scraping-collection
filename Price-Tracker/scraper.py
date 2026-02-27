import logging
import requests
from bs4 import BeautifulSoup
from config import HEADERS



PRICE_SELECTORS = [
    {"name": "x-bin-price__content", "type": "class"},
    {"name": "price", "type": "id"},
    {"name": "span[itemprop='price']", "type": "css"}
]


def extract_price(soup):
    for selector in PRICE_SELECTORS:
        try:
            if selector["type"] == "class":
                element = soup.find(class_=selector["name"])
            elif selector["type"] == "id":
                element = soup.find(id=selector["name"])
            elif selector["type"] == "css":
                element = soup.select_one(selector["name"])

            if element:
                raw = element.get_text()
                cleaned = (
                    raw.replace("EUR", "")
                       .replace("€", "")
                       .replace("$", "")
                       .replace(",", ".")
                       .strip()
                )
                return float(cleaned)
        except Exception:
            continue

    return None


def get_price(session, url):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            logging.warning(f"Bad status code: {response.status_code}")
            return None

        if "captcha" in response.text.lower():
            logging.error("CAPTCHA detected.")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        return extract_price(soup)

    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return None
