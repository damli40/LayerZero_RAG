# rag/rerank.py

import os
import math
from typing import List, Dict, Any
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


def _env_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_rerank_enabled() -> bool:
    # Temporarily disabled to reduce RAM usage in production.
    return False


class BGEReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize BGE reranker for improving search result relevance.
        Lazily loads the CrossEncoder only when enabled.
        """
        self.model_name = model_name
        self.cross_encoder = None
        if is_rerank_enabled():
            try:
                # Lazy import to avoid heavy deps on startup
                from sentence_transformers import CrossEncoder  # type: ignore
                self.cross_encoder = CrossEncoder(model_name)
            except Exception:
                # Fall back silently to no-op reranker
                self.cross_encoder = None
        
    def rerank_documents(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 4,
        confidence_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to query.
        
        Args:
            query: User query
            documents: List of documents to rerank
            top_k: Number of top documents to return
            confidence_threshold: Minimum confidence score threshold
            
        Returns:
            List of reranked documents with confidence scores and metadata
        """
        if not documents:
            return []
            
        # No-op reranker if model is unavailable: assign neutral confidence
        if self.cross_encoder is None:
            fallback_results: List[Dict[str, Any]] = []
            for i, doc in enumerate(documents[: max(top_k, 1)]):
                fallback_results.append({
                    "document": doc,
                    "confidence": 0.5,
                    "rank": i + 1,
                    "source": doc.metadata.get("source", "Unknown"),
                    "source_type": doc.metadata.get("source_type", "Unknown"),
                    "doc_id": doc.metadata.get("doc_id", "Unknown"),
                })
            return fallback_results

        # Prepare pairs for cross-encoder
        pairs = [(query, doc.page_content) for doc in documents]

        # Get relevance scores
        scores = self.cross_encoder.predict(pairs)

        # Create results with metadata
        results: List[Dict[str, Any]] = []
        for i, (doc, score) in enumerate(zip(documents, scores)):
            # Map cross-encoder score to [0,1] via sigmoid for guardrail compatibility
            try:
                confidence = 1.0 / (1.0 + math.exp(-float(score)))
            except Exception:
                confidence = float(score)

            # Only include documents above confidence threshold
            if confidence >= confidence_threshold:
                results.append(
                    {
                        "document": doc,
                        "confidence": confidence,
                        "rank": i + 1,
                        "source": doc.metadata.get("source", "Unknown"),
                        "source_type": doc.metadata.get("source_type", "Unknown"),
                        "doc_id": doc.metadata.get("doc_id", "Unknown"),
                    }
                )
        
        # Sort by confidence score (descending)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Return top_k results
        return results[:top_k]
    
    def get_confidence_score(self, query: str, document_content: str) -> float:
        """
        Get confidence score for a single query-document pair.
        
        Args:
            query: User query
            document_content: Document content
            
        Returns:
            Confidence score between 0 and 1
        """
        if self.cross_encoder is None:
            # Neutral confidence when reranker is disabled
            return 0.5
        score = self.cross_encoder.predict([(query, document_content)])
        try:
            return 1.0 / (1.0 + math.exp(-float(score[0])))
        except Exception:
            return float(score[0])

# Global reranker instance
_reranker = None

def get_reranker() -> BGEReranker:
    """Get or create global reranker instance."""
    global _reranker
    if _reranker is None:
        _reranker = BGEReranker()
    return _reranker

def rerank_documents(
    query: str, 
    documents: List[Document], 
    top_k: int = 4,
    confidence_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Convenience function to rerank documents.
    
    Args:
        query: User query
        documents: List of documents to rerank
        top_k: Number of top documents to return
        confidence_threshold: Minimum confidence score threshold
        
    Returns:
        List of reranked documents with confidence scores and metadata
    """
    reranker = get_reranker()
    return reranker.rerank_documents(query, documents, top_k, confidence_threshold) 