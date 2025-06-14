"""
Sentiment Analysis Module
------------------------
Assigns sentiment scores (1-100) and extracts justifications for forum post tone.
Default: Hugging Face 'ProsusAI/finbert' sentiment pipeline tuned for financial text.

- Modular, production-grade.
- Extendable to FinBERT or financial domain models as needed.
"""
from typing import List, Dict, Tuple
from transformers import pipeline
import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SentimentAnalyzer:
    """
    Sentiment analyzer for forum posts, returns score [1-100] and explanation.
    """
    def __init__(self, model_name: str = "ProsusAI/finbert", device: int = -1):
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=device)
            logger.info(f"Loaded sentiment analysis model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentiment model {model_name}: {e}")
            raise

    def score(self, text: str) -> Tuple[int, str]:
        """
        Assigns a 1-100 sentiment score and a justification.
        Args:
            text (str): Forum post text.
        Returns:
            Tuple[int, str]: (score 1-100, justification string)
        """
        try:
            result = self.sentiment_pipeline(text[:400])  # Model max token limit
            label = result[0]['label']
            score = result[0]['score']

            pos_words = {"growth", "profit", "strong", "improve", "positive", "gain"}
            neg_words = {"loss", "decline", "risk", "weak", "negative", "drop"}
            words = set(re.findall(r"\b\w+\b", text.lower()))
            if label == 'POSITIVE':
                scaled = int(50 + 50 * score)
                hits = list(words & pos_words)
                justification = f"Positive tone (confidence: {score:.2f}); key words: {', '.join(hits[:3])}"
            elif label == 'NEGATIVE':
                scaled = int(50 - 50 * score)
                hits = list(words & neg_words)
                justification = f"Negative tone (confidence: {score:.2f}); key words: {', '.join(hits[:3])}"
            else:
                scaled = 50
                justification = "Neutral tone"
            return scaled, justification
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 50, "Sentiment unavailable"

    def batch_score(self, posts: List[str]) -> List[Dict]:
        """
        Batch scoring for multiple posts.
        Args:
            posts (List[str]): List of forum post texts.
        Returns:
            List[Dict]: [{'text': ..., 'score': ..., 'justification': ...}]
        """
        results = []
        for text in posts:
            score, justification = self.score(text)
            results.append({'text': text, 'score': score, 'justification': justification})
        return results

# Example usage:
# sa = SentimentAnalyzer()
# out = sa.score("Company is showing strong growth and management is visionary.")
# batch = sa.batch_score(["Good results.", "Weak quarter."])

