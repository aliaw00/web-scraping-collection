import logging
from database import init_db, insert_articles
from scraper import NewsScraper
from analyzer import SentimentAnalyzer

# Configure pipeline logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Executes the News Sentiment Pipeline:
    1. Initializes SQLite tables.
    2. Scrapes the feeds (Extract).
    3. Runs VADER sentiment analysis on article titles (Transform).
    4. Writes unique articles into the SQLite database (Load).
    """
    logger.info("Starting News Sentiment Analyzer Pipeline...")
    
    # 1. Initialize DB structure
    init_db()
    
    # 2. Scrape latest feed data
    scraper = NewsScraper()
    raw_articles = scraper.fetch_all_sources()
    
    if not raw_articles:
        logger.warning("No news articles extracted. Exiting pipeline.")
        return

    # 3. Analyze sentiment
    logger.info("Initializing Sentiment Analyzer...")
    analyzer = SentimentAnalyzer()
    
    processed_articles = []
    for article in raw_articles:
        # We analyze the headline (title) as it contains the key sentiment
        sentiment = analyzer.analyze(article["title"])
        
        # Merge sentiment data into the article dict
        article["sentiment_score"] = sentiment["compound"]
        article["sentiment_label"] = sentiment["label"]
        processed_articles.append(article)

    # 4. Insert records into DB
    logger.info(f"Saving {len(processed_articles)} articles to the database...")
    insert_articles(processed_articles)
    logger.info("Pipeline executed successfully!")

if __name__ == "__main__":
    run_pipeline()
