"""
Sentiment Analysis Module
------------------------
Assigns sentiment scores (1-100) and extracts justifications for forum post tone.
Default: Hugging Face 'distilbert-base-uncased-finetuned-sst-2-english' sentiment pipeline.

- Modular, production-grade.
- Extendable to FinBERT or financial domain models as needed.
"""
from typing import List, Dict, Tuple
from transformers import pipeline
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SentimentAnalyzer:
    """
    Sentiment analyzer for forum posts, returns score [1-100] and explanation.
    """
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english", device: int = -1):
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
            if label == 'POSITIVE':
                scaled = int(50 + 50 * score)  # 50-100
                justification = f"Positive tone (confidence: {score:.2f})"
            elif label == 'NEGATIVE':
                scaled = int(50 - 50 * score)  # 1-50
                justification = f"Negative tone (confidence: {score:.2f})"
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

