"""
Knowledge Graph Construction Module
----------------------------------
Builds and updates a property graph (Neo4j) to capture companies, metrics, sentiment, and relationships.
- Modular and production-grade
- Uses py2neo for Neo4j operations
"""
from typing import Dict, List, Optional
from py2neo import Graph, Node, Relationship
from utils.logger import setup_logger

logger = setup_logger(__name__)

class KnowledgeGraphBuilder:
    """
    Builds and updates the knowledge graph for stocks, metrics, sentiment, and peer links.
    """
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.graph = Graph(uri, auth=(user, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            raise

    def upsert_company(self, symbol: str, name: Optional[str] = None, sector: Optional[str] = None):
        """
        Ensures a Company node exists (creates or updates).
        """
        try:
            company = Node("Company", symbol=symbol, name=name, sector=sector)
            self.graph.merge(company, "Company", "symbol")
            logger.info(f"Upserted company: {symbol}")
        except Exception as e:
            logger.error(f"Failed to upsert company {symbol}: {e}")

    def add_metric(self, symbol: str, metric: str, value):
        """
        Adds/updates a Metric node and links it to the company.
        """
        try:
            metric_node = Node("Metric", name=metric, value=value)
            self.graph.merge(metric_node, "Metric", ["name", "value"])
            company = self.graph.nodes.match("Company", symbol=symbol).first()
            if company:
                rel = Relationship(company, "HAS_METRIC", metric_node)
                self.graph.merge(rel)
                logger.info(f"Linked {symbol} to metric {metric}={value}")
        except Exception as e:
            logger.error(f"Failed to add metric {metric} for {symbol}: {e}")

    def add_sentiment(self, symbol: str, month: str, score: int):
        """
        Adds a Sentiment node for a company/month and links it.
        """
        try:
            sent_node = Node("Sentiment", month=month, score=score)
            self.graph.merge(sent_node, "Sentiment", ["month", "score"])
            company = self.graph.nodes.match("Company", symbol=symbol).first()
            if company:
                rel = Relationship(company, "HAS_SENTIMENT", sent_node)
                self.graph.merge(rel)
                logger.info(f"Linked {symbol} to sentiment {score} for {month}")
        except Exception as e:
            logger.error(f"Failed to add sentiment for {symbol} {month}: {e}")

    def add_peer_link(self, symbol1: str, symbol2: str):
        """
        Adds a COMPETES_WITH relationship between two companies.
        """
        try:
            c1 = self.graph.nodes.match("Company", symbol=symbol1).first()
            c2 = self.graph.nodes.match("Company", symbol=symbol2).first()
            if c1 and c2:
                rel = Relationship(c1, "COMPETES_WITH", c2)
                self.graph.merge(rel)
                logger.info(f"Linked {symbol1} <-> {symbol2} as peers")
        except Exception as e:
            logger.error(f"Failed to add peer link {symbol1}-{symbol2}: {e}")

    def query_company_metrics(self, symbol: str) -> List[Dict]:
        """
        Returns all metrics for a company.
        """
        try:
            query = (
                "MATCH (c:Company {symbol: $symbol})-[:HAS_METRIC]->(m:Metric) "
                "RETURN m.name as metric, m.value as value"
            )
            result = self.graph.run(query, symbol=symbol).data()
            logger.info(f"Queried metrics for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Failed to query metrics for {symbol}: {e}")
            return []

# Example usage:
# kg = KnowledgeGraphBuilder(uri="bolt://localhost:7687", user="neo4j", password="password")
# kg.upsert_company("RELIANCE", name="Reliance Industries", sector="Conglomerate")
# kg.add_metric("RELIANCE", "ROCE", 18.4)
# kg.add_sentiment("RELIANCE", "2024-06", 82)
# kg.add_peer_link("RELIANCE", "IOC")
# print(kg.query_company_metrics("RELIANCE"))
# kg_builder.py

