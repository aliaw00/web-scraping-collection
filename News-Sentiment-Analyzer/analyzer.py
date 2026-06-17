import nltk
import logging
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Configure simple logging
logging.basicConfig(level=logging.INFO)

# Attempt to download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except Exception as e:
        logging.warning(f"Could not download NLTK vader_lexicon. Falling back to rule-based classification. Error: {e}")

class SentimentAnalyzer:
    """
    Handles sentiment classification using NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner).
    Includes a robust dictionary-based fallback system in case VADER dependencies fail to load.
    """
    def __init__(self):
        try:
            self.sia = SentimentIntensityAnalyzer()
            self.use_vader = True
            logging.info("VADER Sentiment Analyzer initialized successfully.")
        except Exception as e:
            self.use_vader = False
            logging.warning(f"VADER initialization failed. Using rule-based fallback. Details: {e}")
            
            # Simple rule-based lexicon for fallback analysis
            self.pos_words = {
                'boost', 'surge', 'gain', 'gains', 'growth', 'positive', 'good', 'high', 
                'success', 'win', 'wins', 'rise', 'rises', 'up', 'bullish', 'optimism', 
                'advance', 'strengthen', 'improvement', 'happy', 'innovative', 'breakthrough', 
                'support', 'peace', 'agreement', 'healthy', 'secure', 'recovery', 'recovers'
            }
            self.neg_words = {
                'drop', 'plunge', 'fall', 'falls', 'loss', 'losses', 'negative', 'bad', 
                'low', 'failure', 'lose', 'loses', 'down', 'crash', 'bearish', 'war', 
                'crisis', 'decline', 'declines', 'scandal', 'fear', 'conflict', 'concern', 
                'alert', 'risk', 'fail', 'fails', 'tension', 'death', 'kill', 'killed', 
                'threat', 'inflation', 'recession', 'warning', 'disaster'
            }

    def analyze(self, text: str) -> dict:
        """
        Calculates sentiment for a given text.
        
        Args:
            text (str): Title or text summary to analyze.
            
        Returns:
            dict: { 'compound': float (-1.0 to 1.0), 'label': str ('Positive', 'Negative', 'Neutral') }
        """
        if not text or not isinstance(text, str):
            return {'compound': 0.0, 'label': 'Neutral'}

        compound = 0.0
        if self.use_vader:
            try:
                scores = self.sia.polarity_scores(text)
                compound = scores['compound']
            except Exception as e:
                logging.warning(f"VADER analysis failed, falling back. Error: {e}")
                compound = self._fallback_analyze(text)
        else:
            compound = self._fallback_analyze(text)

        # Classify sentiment labels based on standard compound thresholds
        if compound >= 0.05:
            label = 'Positive'
        elif compound <= -0.05:
            label = 'Negative'
        else:
            label = 'Neutral'

        return {
            'compound': round(compound, 4),
            'label': label
        }

    def _fallback_analyze(self, text: str) -> float:
        """
        Simple keyword-matching sentiment scoring as a fallback.
        """
        words = [w.strip(".,!?\"'()[]{}") for w in text.lower().split()]
        pos_count = sum(1 for w in words if w in self.pos_words)
        neg_count = sum(1 for w in words if w in self.neg_words)
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        return (pos_count - neg_count) / total
