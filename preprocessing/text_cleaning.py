"""
Text Preprocessing Module
------------------------
Cleans and normalizes raw forum post text for downstream NLP tasks.
- Modular and production-grade
- Easily extended for extra cleaning, language detection, or normalization steps
"""
from typing import List
import re
import unicodedata
import spacy
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TextPreprocessor:
    """
    Cleans and preprocesses text: lowercasing, punctuation, stopword removal, lemmatization, etc.
    """
    def __init__(self, language: str = "en"):
        self.language = language
        try:
            self.nlp = spacy.load("en_core_web_sm") if language == "en" else spacy.blank(language)
        except Exception as e:
            logger.error(f"Failed to load spaCy model for language '{language}': {e}")
            raise

    def clean_text(self, text: str) -> str:
        """
        Normalize, lowercase, and remove unwanted characters.
        """
        text = unicodedata.normalize("NFKC", text)
        text = text.lower()
        text = re.sub(r"\s+", " ", text)           # Collapse whitespace
        text = re.sub(r"http\S+", "", text)        # Remove URLs
        text = re.sub(r"[^\w\s.,!?]", "", text)   # Remove special chars except basic punct.
        return text.strip()

    def tokenize_lemmatize(self, text: str) -> List[str]:
        """
        Tokenize and lemmatize using spaCy, removing stopwords and punctuation.
        """
        doc = self.nlp(text)
        return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.lemma_]

    def preprocess(self, text: str) -> str:
        """
        Full pipeline: clean, tokenize, lemmatize, and rejoin.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize_lemmatize(cleaned)
        return " ".join(tokens)

# Example usage:
# pre = TextPreprocessor()
# out = pre.preprocess("Forum text... with lots of  Stuff! Visit http://... ")
# logger.info(f"Preprocessed text: {out}")
# text_cleaning.py

