# rag/rerank.py

import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class BGEReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        Initialize BGE reranker for improving search result relevance.
        
        Args:
            model_name: BGE reranker model to use
        """
        self.model_name = model_name
        self.cross_encoder = CrossEncoder(model_name)
        
    def rerank_documents(
        self, 
        query: str, 
        documents: List[Document], 
        top_k: int = 4,
        confidence_threshold: float = 0.5
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
            
        # Prepare pairs for cross-encoder
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Get relevance scores
        scores = self.cross_encoder.predict(pairs)
        
        # Create results with metadata
        results = []
        for i, (doc, score) in enumerate(zip(documents, scores)):
            confidence = float(score)
            
            # Only include documents above confidence threshold
            if confidence >= confidence_threshold:
                results.append({
                    "document": doc,
                    "confidence": confidence,
                    "rank": i + 1,
                    "source": doc.metadata.get("source", "Unknown"),
                    "source_type": doc.metadata.get("source_type", "Unknown"),
                    "doc_id": doc.metadata.get("doc_id", "Unknown")
                })
        
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
        score = self.cross_encoder.predict([(query, document_content)])
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