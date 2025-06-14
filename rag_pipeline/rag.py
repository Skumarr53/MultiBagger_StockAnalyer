"""
RAG Pipeline Module
------------------
Implements a Retrieval-Augmented Generation (RAG) system:
- Stores monthly summaries in a vector database (FAISS or Chroma)
- Enables semantic search and context-aware LLM answers
- Modular, production-grade, easily extensible
"""
from typing import List, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from utils.logger import setup_logger

logger = setup_logger(__name__)

class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline: semantic search + LLM answer.
    """
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", llm_model_name: str = "facebook/bart-large-cnn", device: Optional[int] = None):
        try:
            self.embedder = SentenceTransformer(embedding_model_name)
            logger.info(f"Loaded embedding model: {embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedder: {e}")
            raise
        try:
            self.llm = pipeline("summarization", model=llm_model_name, device=device if device is not None else -1)
            logger.info(f"Loaded LLM: {llm_model_name}")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            raise
        self.docs = []  # List[str]: stores text chunks
        self.doc_metadata = []  # List[dict]: metadata (e.g., month, company)
        self.index = None

    def add_documents(self, docs: List[str], metadatas: List[dict]):
        """
        Adds documents to the vector store, builds/updates FAISS index.
        Args:
            docs: list of doc strings (e.g., monthly summaries)
            metadatas: list of dict metadata for each doc
        """
        self.docs.extend(docs)
        self.doc_metadata.extend(metadatas)
        # Compute embeddings and build/update FAISS index
        embeddings = self.embedder.encode(self.docs, convert_to_numpy=True, show_progress_bar=True)
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        logger.info(f"Indexed {len(self.docs)} documents in vector store.")

    def semantic_search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Returns top_k most similar docs to query.
        Args:
            query: query string
            top_k: number of matches to return
        Returns:
            List[dict]: [{"text":..., "metadata":...}]
        """
        if not self.index or not self.docs:
            logger.warning("No docs in index.")
            return []
        emb = self.embedder.encode([query], convert_to_numpy=True)
        D, I = self.index.search(emb, top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.docs):
                results.append({"text": self.docs[idx], "metadata": self.doc_metadata[idx]})
        logger.info(f"Semantic search found {len(results)} results.")
        return results

    def rag_answer(self, query: str, top_k: int = 3) -> str:
        """
        Returns an LLM-generated answer/context-aware summary using top docs.
        Args:
            query: user query string
            top_k: number of top docs to include as context
        Returns:
            str: LLM-generated answer
        """
        top_docs = self.semantic_search(query, top_k=top_k)
        context = " ".join([doc["text"] for doc in top_docs])
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        try:
            summary = self.llm(prompt, max_length=180, min_length=30, do_sample=False)
            answer = summary[0]["summary_text"]
            logger.info("Generated RAG answer.")
            return answer
        except Exception as e:
            logger.error(f"RAG answer generation failed: {e}")
            return "Answer unavailable."

# Example usage:
# rag = RAGPipeline()
# rag.add_documents(["Summary 1...", "Summary 2..."], [{"month": "2024-06", "company": "RELIANCE"}, ...])
# print(rag.semantic_search("What is the outlook for Reliance?"))
# print(rag.rag_answer("Best smallcap opportunities in chemicals?"))
# rag.py

