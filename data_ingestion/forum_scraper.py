"""
ValuePickr Forum Scraper
------------------------
Production-grade module to fetch threads and posts from the Stock Opportunities category.
Designed for maintainability, modularity, and robust error handling.
"""
import re
from typing import List, Dict, Optional
import requests
from datetime import datetime
from utils.logger import setup_logger
from config import forum_cfg, companies_suffix
from tqdm import tqdm
logger = setup_logger(__name__)

class ValuePickrForumScraper:
    """
    Scrapes threads and posts from ValuePickr Stock Opportunities forum.
    """
    def __init__(self, base_url: str = "https://forum.valuepickr.com/c/stock-opportunities"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}.json"
        self.session = requests.Session()
        self.comp_suffixes = set(companies_suffix)
        logger.info(f"Initialized scraper for {self.base_url}")
    
    def extract_company_from_title(self, title: str) -> str:
        # Split on common separators
        base = re.split(r"[-~:]", title, maxsplit=1)[0]
        # Remove content in parentheses only if it appears after company base
        base = re.split(r"\(", base)[0]
        # Remove leading/trailing whitespace and common words
        base = base.strip().replace("  ", " ")

        # If the base ends with one of our suffixes, keep as is.
        # Otherwise, try to extend base to include suffix if present in title
        for suffix in self.comp_suffixes:
            if suffix.lower() in base.lower():
                # Rebuild base to the point where suffix occurs
                match = re.search(rf'(.+?\s*{suffix})', base, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        # Title-case for readability (can be changed as needed)
        return base.title()

    def fetch_threads(self, max_pages: int = 5) -> List[Dict]:
        """
        Fetch list of threads (topics) from the Stock Opportunities category (paginated).
        Args:
            max_pages (int): Number of forum pages to fetch.
        Returns:
            List[Dict]: List of thread metadata dicts.
        """
        threads = []
        
        logger.info(f"Fetching threads from {self.api_url} (max {max_pages} pages)")
        for page in tqdm(range(0, 100)):
            url = f"{self.api_url}?page={page + 1}"
            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                page_threads = data.get('topic_list', {}).get('topics', [])
                threads.extend(page_threads)
                logger.info(f"Fetched {len(page_threads)} threads from page {page + 1}")
                if not page_threads:
                    break
            except Exception as e:
                logger.error(f"Failed to fetch threads from {url}: {e}")
                break
        return threads

    def fetch_posts(self, thread_id: int) -> List[Dict]:
        """
        Fetches all posts for a given thread.
        Args:
            thread_id (int): Topic/thread ID.
        Returns:
            List[Dict]: List of post dicts.
        """
        posts = []
        url = f"https://forum.valuepickr.com/t/{thread_id}.json"
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            posts = data.get('post_stream', {}).get('posts', [])
            logger.info(f"Fetched {len(posts)} posts for thread {thread_id}")
        except Exception as e:
            logger.error(f"Failed to fetch posts for thread {thread_id}: {e}")
        return posts

    def scrape_company_monthly_posts(self) -> Dict[str, List[Dict]]:
        """
        Aggregates all posts by month (YYYY-MM).
        Args:
            max_threads (Optional[int]): Limit threads to process for demo/perf.
        Returns:
            Dict[str, List[Dict]]: {YYYY-MM: [posts]}
        """
        threads = self.fetch_threads()
        company_posts = {}  # {company: {month: [posts]}}
        
        threads = threads[forum_cfg.max_threads] if hasattr(forum_cfg, 'max_threads') else threads
        
        logger.info(f"Processing {len(threads)} threads for monthly aggregation")
        for thread in tqdm(threads):
            title = thread.get("title", "")
            company = self.extract_company_from_title(title)
            print(f"Processing for company: {company}")
            thread_id = thread.get('id')
            if thread_id is None: continue
            posts = self.fetch_posts(thread_id)
            
            for post in posts:
                created_at = post.get('created_at')
                if not created_at: continue
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                month_key = dt.strftime('%Y-%m')
                company_posts.setdefault(company, {}).setdefault(month_key, []).append(post)

                # if month_key not in company_posts:
                #     company_posts[month_key] = []
                # company_posts[month_key].append(post)
        logger.info(f"Aggregated posts by month: {[(k, len(v)) for k,v in company_posts.items()]}")
        return company_posts

# Example usage:
# scraper = ValuePickrForumScraper()
# threads = scraper.fetch_threads()
# posts = scraper.fetch_posts(12345)
# monthly = scraper.scrape_monthly_posts(max_threads=5)
# forum_scraper.py

