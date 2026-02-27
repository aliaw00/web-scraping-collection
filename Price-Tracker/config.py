import os
from dotenv import load_dotenv

load_dotenv()

CHECK_INTERVAL_MIN = int(os.getenv("CHECK_INTERVAL_MIN", 60))
CHECK_INTERVAL_MAX = int(os.getenv("CHECK_INTERVAL_MAX", 120))
LOG_FILE = os.getenv("LOG_FILE", "guardian.log")
DB_NAME = os.getenv("DB_NAME", "prices.db")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}
