from scraper.reddit_client import RedditScraper
from database.db_manager import DatabaseManager

def main():
    """
    The ETL Pipeline: Extract (Reddit), Transform (Format Dict), Load (SQLite).
    """
    # 1. Initialize components
    scraper = RedditScraper()
    db = DatabaseManager()
    
    # 2. Define targets
    target_subreddits = ["Python", "learnprogramming", "dataengineering", "artificial"]
    
    # 3. Execute collection
    for sub in target_subreddits:
        try:
            posts = scraper.fetch_hot_posts(subreddit_name=sub, limit=50)
            db.insert_posts(posts)
            print(f"✅ Successfully saved {len(posts)} posts from r/{sub}.")
        except Exception as e:
            print(f"❌ Error fetching from r/{sub}: {e}")

if __name__ == "__main__":
    main()
