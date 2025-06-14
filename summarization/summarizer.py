"""
Summarization Module
-------------------
Production-grade module for abstractive summarization using Hugging Face Transformers.
Default: BART-large (state-of-the-art for English summarization).

Why BART/T5/Pegasus?
- All three are top-performers for abstractive summarization tasks (benchmarked on CNN/DailyMail, XSum, etc.).
- BART: Very strong on forum/news summarization, robust to long/messy text (used by default here).
- T5: Highly flexible, performs well for multi-lingual/transfer cases.
- Pegasus: State-of-the-art for extreme summarization (distills large docs into very short summaries).

Here, BART-large is chosen for default: best results for long-form, discussion-style text, and mature Hugging Face support.
"""
import os
from typing import List, Optional
from transformers import pipeline, Pipeline
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Summarizer:
    """
    Abstractive summarizer for forum discussions, using Hugging Face Transformers.
    """
    def __init__(self, model_name: str = "facebook/bart-large-cnn", device: Optional[int] = None):
        """
        Args:
            model_name: Hugging Face model hub name.
            device: set to -1 for CPU, or 0/1/2... for GPU (if available).
        """
        try:
            model_cache_path = os.path.join(os.path.expanduser("~/.cache/huggingface/hub/models--"), model_name.replace("/", "--"))
            if not os.path.exists(model_cache_path):
                logger.info(f"Model {model_name} not found in cache. Downloading...")
            
            self.summarizer: Pipeline = pipeline(
                "summarization", model=model_name, device=device if device is not None else -1
            )
            logger.info(f"Loaded summarization pipeline with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load summarization model {model_name}: {e}")
            raise

    def summarize_posts(self, posts: List[str], max_length: int = 180, min_length: int = 40) -> str:
        """
        Summarize a list of forum posts into a single monthly summary.
        Args:
            posts (List[str]): List of post texts.
            max_length (int): Max tokens in summary.
            min_length (int): Min tokens in summary.
        Returns:
            str: Abstractive summary.
        """
        text = " ".join(posts)
        if len(text) < 100:
            logger.warning("Not enough text to summarize; returning raw input.")
            return text
        # Hugging Face models have a max token limit (1024 for BART-large)
        text = text[:3500]  # Keep under 1024 tokens roughly
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            result = summary[0]["summary_text"]
            logger.info(f"Generated summary ({len(result.split())} words)")
            return result
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Summary unavailable."

# Example usage:
# s = Summarizer()
# summary = s.summarize_posts(["Forum post 1", "Forum post 2", ...])
