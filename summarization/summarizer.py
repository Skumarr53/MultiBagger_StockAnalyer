"""
Summarization Module
-------------------
Production-grade module for abstractive summarization using Hugging Face Transformers.
Default: Pegasus-XSum which performs well on news/financial text.

Why BART/T5/Pegasus?
- All three are top-performers for abstractive summarization tasks (benchmarked on CNN/DailyMail, XSum, etc.).
- BART: Very strong on forum/news summarization, robust to long/messy text (used by default here).
- T5: Highly flexible, performs well for multi-lingual/transfer cases.
- Pegasus: State-of-the-art for extreme summarization (distills large docs into very short summaries).

Here, Pegasus-XSum is chosen for default: strong results on short news style text, suitable for forum posts.
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
    def __init__(self, model_name: str = "google/pegasus-xsum", device: Optional[int] = None):
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

        # Split text into manageable chunks instead of truncating
        chunk_size = 3000
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        summaries = []
        try:
            for chunk in chunks:
                out = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                summaries.append(out[0]["summary_text"])
            result = " ".join(summaries)
            logger.info(f"Generated summary from {len(chunks)} chunk(s) ({len(result.split())} words)")
            return result
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Summary unavailable."

# Example usage:
# s = Summarizer()
# summary = s.summarize_posts(["Forum post 1", "Forum post 2", ...])
