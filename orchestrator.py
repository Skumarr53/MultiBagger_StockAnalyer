"""
Pipeline Orchestrator
--------------------
Integrates all modules for a full end-to-end run.
- Loads config, fetches data, preprocesses, summarizes, scores sentiment, screens, updates knowledge graph, and refreshes dashboard data
- Modular and ready for production scheduling
"""
import os
from typing import List, Dict
from config import project_cfg, forum_cfg, api_cfg
from data_ingestion.forum_scraper import ValuePickrForumScraper
from preprocessing.text_cleaning import TextPreprocessor
from summarization.summarizer import Summarizer
from sentiment_analysis.sentiment import SentimentAnalyzer
from financial_data.financial_api import FinancialDataFetcher
from screening_ml.screening import StockScreener
from knowledge_graph.kg_builder import KnowledgeGraphBuilder
from rag_pipeline.rag import RAGPipeline
from utils.logger import setup_logger
from utils.env import load_environment

load_environment()
logger = setup_logger(__name__)

class StockAnalysisPipeline:
    def __init__(self):
        self.scraper = ValuePickrForumScraper(base_url=forum_cfg.base_url)
        self.pre = TextPreprocessor()
        self.summarizer = Summarizer()
        self.sa = SentimentAnalyzer()
        self.fetcher = FinancialDataFetcher(os.getenv("EODHD_API_KEY"))
        self.screener = StockScreener()
        self.kg = KnowledgeGraphBuilder(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
        )
        self.rag = RAGPipeline()

    def get_company_posts(self):
        return self.scraper.scrape_company_monthly_posts()

    def process_company_month(self, company, month, posts):
        clean = [self.pre.preprocess(p["cooked"]) for p in posts]
        summary = self.summarizer.summarize_posts(clean)
        sentiments = self.sa.batch_score(clean)
        sentiment_score = int(sum([x["score"] for x in sentiments]) / max(1, len(sentiments)))
        metrics = self.fetcher.fetch_all(company)
        passed = self.screener.filter_stocks([metrics])
        self.kg.upsert_company(company, name=company)
        for m, v in metrics.get("eodhd", {}).items():
            self.kg.add_metric(company, m, v)
        self.kg.add_sentiment(company, month, sentiment_score)
        self.rag.add_documents([summary], [{"company": company, "month": month}])
        logger.info(f"Processed {company} for {month}.")

    def run(self):
        company_posts = self.get_company_posts()
        for company, monthly_posts in company_posts.items():
            for month, posts in monthly_posts.items():
                self.process_company_month(company, month, posts)
        logger.info("Pipeline run complete.")

if __name__ == "__main__":
    pipeline = StockAnalysisPipeline()
    pipeline.run()
    