import os
from dotenv import load_dotenv

# Load env variables from the directory where config.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

# Configuration settings
DB_NAME = os.getenv("DB_NAME", "courses.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
DEFAULT_QUERY = os.getenv("DEFAULT_QUERY", "computer science")

# APIs URL endpoints
COURSERA_API_URL = os.getenv("COURSERA_API_URL", "https://api.coursera.org/api/courses.v1")
STANFORD_API_URL = os.getenv("STANFORD_API_URL", "https://explorecourses.stanford.edu/search")
MIT_OCW_URL = os.getenv("MIT_OCW_URL", "https://ocw.mit.edu/courses/")
