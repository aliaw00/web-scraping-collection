import re
from collections import Counter
import pandas as pd

class TrendAnalyzer:
    """
    Processes text data to extract insights and trending keywords.
    """
    
    # A basic set of English stop words to filter out noise
    STOP_WORDS = {
        'the', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 
        'for', 'on', 'are', 'as', 'with', 'his', 'they', 'I', 'of', 'and',
        'this', 'how', 'what', 'why', 'can', 'do', 'my', 'we', 'from', 'at'
    }

    @staticmethod
    def extract_top_keywords(titles: pd.Series, top_n: int = 20) -> pd.DataFrame:
        """
        Tokenizes text, removes stop words, and counts frequencies.
        """
        all_words = []
        
        for title in titles:
            # Lowercase and extract only alphabetic words
            words = re.findall(r'\b[a-z]{3,}\b', str(title).lower())
            # Filter out stop words
            filtered_words = [w for w in words if w not in TrendAnalyzer.STOP_WORDS]
            all_words.extend(filtered_words)
            
        # Count word occurrences
        word_counts = Counter(all_words)
        
        # Convert to DataFrame for easy Plotly integration
        df_trends = pd.DataFrame(word_counts.most_common(top_n), columns=['Keyword', 'Mentions'])
        return df_trends
