# rag/query_rag.py

import os
import time
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient

# Import our new modules
from rag.rerank import rerank_documents, is_rerank_enabled
from rag.guardrails import get_guardrails, ToolCategory
from rag.metadata_db import get_metadata_db

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

def get_relevant_documents(query: str, k: int = 8) -> List[Document]:
    """
    Get relevant documents from vector store with enhanced retrieval.
    
    Args:
        query: User query
        k: Number of documents to retrieve (increased for reranking)
        
    Returns:
        List of relevant documents
    """
    # Use text-embedding-3-large
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=3072
    )

    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    qdrant_vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=QDRANT_COLLECTION_NAME,
        embeddings=embeddings,
    )

    retriever = qdrant_vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)

def build_metaprompt(question: str, docs: List[Document], sources: List[Dict]) -> str:
    """
    Build enhanced metaprompt with source information.
    
    Args:
        question: User question
        docs: Retrieved documents
        sources: Source metadata with confidence scores
        
    Returns:
        Formatted prompt
    """
    context_parts = []
    
    for i, (doc, source) in enumerate(zip(docs, sources)):
        confidence = source.get("confidence", 0.0)
        source_name = source.get("source", "Unknown")
        
        context_parts.append(f"[Source {i+1}: {source_name} (confidence: {confidence:.2f})]\n{doc.page_content}")
    
    context = "\n\n".join(context_parts)
    
    return f"""
You are a knowledgeable assistant for the LayerZero ecosystem.
Use the following context to answer the user's question.
If the answer is not found in the context, say "I don't know".
Always provide accurate information based on the provided sources.

Context:
{context}

Question: {question}

Answer:"""

def query_rag(
    question: str, 
    user_id: Optional[str] = None,
    client_type: str = "web",
    k: int = 4,
    confidence_threshold: float = 0.5
) -> Dict[str, any]:
    """
    Enhanced RAG query with guardrails, reranking, and metadata tracking.
    
    Args:
        question: User question
        user_id: Optional user identifier
        client_type: Type of client (web, telegram, etc.)
        k: Number of documents to return
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        Dictionary with response, metadata, and guardrail info
    """
    start_time = time.time()
    
    # Initialize components
    guardrails = get_guardrails()
    metadata_db = get_metadata_db()
    
    # Generate response ID
    response_id = guardrails.generate_response_id(question, user_id or "anonymous")
    
    # Guardrail checks
    rate_limit_allowed, rate_limit_msg = guardrails.check_rate_limit(user_id or "anonymous")
    if not rate_limit_allowed:
        return {
            "response": f"Rate limit exceeded: {rate_limit_msg}",
            "success": False,
            "error": "rate_limit",
            "response_id": response_id
        }
    
    safety_allowed, safety_msg = guardrails.check_content_safety(question)
    if not safety_allowed:
        return {
            "response": f"Content safety check failed: {safety_msg}",
            "success": False,
            "error": "content_safety",
            "response_id": response_id
        }
    
    # Classify prompt and validate tool access
    prompt_category = guardrails.classify_prompt(question)
    allowed_tools = guardrails.get_allowed_tools_for_prompt(question)
    
    if ToolCategory.RAG_QUERY not in allowed_tools:
        return {
            "response": "This type of query is not allowed with the current tool set.",
            "success": False,
            "error": "tool_access",
            "response_id": response_id
        }
    
    try:
        # Retrieve documents
        docs = get_relevant_documents(question, k=k*2)  # Get more for reranking
        
        if not docs:
            return {
                "response": "I couldn't find any relevant information in the knowledge base.",
                "success": False,
                "error": "no_documents",
                "response_id": response_id,
                "confidence_score": 0.0,
                "sources": []
            }
        
        # Rerank documents (or fallback if disabled)
        reranked_results = rerank_documents(
            query=question,
            documents=docs,
            top_k=k,
            confidence_threshold=confidence_threshold,
        )
        
        if not reranked_results:
            return {
                "response": "I couldn't find any sufficiently relevant information for your query.",
                "success": False,
                "error": "low_confidence",
                "response_id": response_id,
                "confidence_score": 0.0,
                "sources": []
            }
        
        # Extract documents and sources
        reranked_docs = [result["document"] for result in reranked_results]
        sources = [{
            "source": result["source"],
            "source_type": result["source_type"],
            "doc_id": result["doc_id"],
            "confidence": result["confidence"],
            "rank": result["rank"]
        } for result in reranked_results]
        
        # Calculate overall confidence
        overall_confidence = sum(result["confidence"] for result in reranked_results) / len(reranked_results)
        
        # Build enhanced prompt
        metaprompt = build_metaprompt(question, reranked_docs, sources)
        
        # Generate response
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        llm_response = llm.invoke(metaprompt)
        response_text = llm_response.content
        
        # Add source citations
        citations = guardrails.format_source_citations(sources)
        response_with_citations = response_text + citations
        
        # Sanitize response
        sanitized_response = guardrails.sanitize_response(response_with_citations)
        
        # Validate response
        response_valid, validation_msg = guardrails.validate_response(
            sanitized_response, overall_confidence, sources
        )
        
        if not response_valid:
            return {
                "response": f"Response validation failed: {validation_msg}",
                "success": False,
                "error": "validation",
                "response_id": response_id
            }
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log to metadata database
        query_id = metadata_db.log_query(
            query_text=question,
            user_id=user_id,
            client_type=client_type,
            confidence_score=overall_confidence,
            response_length=len(sanitized_response),
            sources_used=sources,
            processing_time_ms=processing_time_ms
        )
        
        # Log tool usage
        metadata_db.log_tool_usage(
            query_id=query_id,
            tool_name="rag_query",
            tool_category="rag_query"
        )
        
        return {
            "response": sanitized_response,
            "success": True,
            "response_id": response_id,
            "confidence_score": overall_confidence,
            "sources": sources,
            "processing_time_ms": processing_time_ms,
            "prompt_category": prompt_category.value
        }
        
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log error to metadata database
        metadata_db.log_query(
            query_text=question,
            user_id=user_id,
            client_type=client_type,
            confidence_score=0.0,
            response_length=0,
            sources_used=[],
            processing_time_ms=processing_time_ms
        )
        
        return {
            "response": f"An error occurred while processing your query: {str(e)}",
            "success": False,
            "error": "processing_error",
            "response_id": response_id,
            "processing_time_ms": processing_time_ms
        }

# Backward compatibility function
def ask_question(question: str) -> str:
    """
    Backward compatibility function for existing code.
    
    Args:
        question: User question
        
    Returns:
        Response text
    """
    result = query_rag(question)
    return result.get("response", "An error occurred.")

# Example usage
if __name__ == "__main__":
    user_question = input("Ask a question: ")
    print("\n🧠 Answer:")
    result = query_rag(user_question)
    print(result["response"])
    if result.get("confidence_score"):
        print(f"\nConfidence: {result['confidence_score']:.2f}")
