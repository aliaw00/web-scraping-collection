import praw
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RedditScraper:
    """
    A client wrapper for the PRAW library. 
    Isolates external API logic from the rest of the application.
    """
    
    def __init__(self):
        # Initializes PRAW using credentials from the environment
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    def fetch_hot_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict]:
        """
        Fetches the top 'hot' posts from a specific subreddit.
        
        Args:
            subreddit_name (str): The name of the subreddit (e.g., 'Python').
            limit (int): Maximum number of posts to fetch.
            
        Returns:
            List[Dict]: A list of dictionaries containing standardized post data.
        """
        print(f"Fetching up to {limit} posts from r/{subreddit_name}...")
        subreddit = self.reddit.subreddit(subreddit_name)
        
        posts_data = []
        for post in subreddit.hot(limit=limit):
            # Skip stickied posts (usually rules/announcements)
            if post.stickied:
                continue
                
            posts_data.append({
                "id": post.id,
                "subreddit": subreddit_name,
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "url": post.url
            })
            
        return posts_data
