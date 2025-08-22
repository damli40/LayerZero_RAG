# rag/query_rag.py

import os
import sys
import math
import time
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient

# Import our new modules
try:
    # Ensure project root on sys.path when running directly (python rag/query.py)
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
except Exception:
    pass

from rag.rerank import rerank_documents, is_rerank_enabled
from rag.guardrails import get_guardrails, ToolCategory
from rag.metadata_db import get_metadata_db
from rag.utils.glossary import augment_query_for_retrieval, find_glossary_expansions

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "layerzero-rag")

def check_qdrant_ready() -> Dict[str, any]:
    """Lightweight readiness check for Qdrant connectivity."""
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        # Simple call to verify connectivity
        client.get_collections()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def get_relevant_documents(query: str, k: int = 8, use_mmr: bool = True) -> List[Document]:
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

    if use_mmr:
        # Maximal Marginal Relevance for diversity
        retriever = qdrant_vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": max(32, k * 6),
                "lambda_mult": 0.55,
            },
        )
    else:
        retriever = qdrant_vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)


def _build_clarifying_question(
    original_question: str,
    expansions: Dict[str, List[str]] | Dict[str, any],
    candidate_docs: List[Document]
) -> str:
    """
    Compose a short clarifying question using glossary matches and top document metadata.
    """
    # Collect possible topics from glossary canonical terms
    topic_candidates: List[str] = []
    try:
        topic_candidates.extend(list(expansions.keys()))
    except Exception:
        pass

    # Add titles/section paths from candidate docs
    for d in candidate_docs[:5]:
        title = d.metadata.get("title")
        section = d.metadata.get("section_path")
        source = d.metadata.get("source")
        if title and title not in topic_candidates:
            topic_candidates.append(title)
        if section and section not in topic_candidates:
            topic_candidates.append(section)
        if source and source not in topic_candidates:
            topic_candidates.append(source)

    # Deduplicate and take top few
    seen = set()
    unique_topics: List[str] = []
    for t in topic_candidates:
        if not t:
            continue
        t_norm = t.strip()
        if t_norm and t_norm.lower() not in seen:
            seen.add(t_norm.lower())
            unique_topics.append(t_norm)
        if len(unique_topics) >= 3:
            break

    if unique_topics:
        options = ", ".join(unique_topics)
        return f"I need a bit more detail to help. Do you mean: {options}?"
    return "Could you clarify what you want to know specifically? For example: protocol overview, endpoints, or DVN."

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
        # Augment query with domain synonyms/aliases for better recall
        augmented_question = augment_query_for_retrieval(question)
        expansions, _matched = find_glossary_expansions(question)

        # Build multiple query variants: original, augmented, and canonical-term variants
        query_variants: List[str] = []
        base_q = question.strip()
        if base_q:
            query_variants.append(base_q)
        if augmented_question and augmented_question != base_q:
            query_variants.append(augmented_question)
        for canonical in expansions.keys():
            variant = f"{base_q} {canonical}".strip()
            if variant and variant not in query_variants:
                query_variants.append(variant)

        # Limit number of variants to control latency
        query_variants = query_variants[:5]

        # Retrieve for each variant and merge unique results
        combined_docs: List[Document] = []
        seen_keys = set()

        total_candidates = max(k * 6, 24)
        per_variant_k = max(2, math.ceil(total_candidates / max(1, len(query_variants))))

        for q in query_variants:
            variant_docs = get_relevant_documents(q, k=per_variant_k)
            for d in variant_docs:
                doc_id = d.metadata.get("document_id") or d.metadata.get("doc_id") or d.metadata.get("source") or ""
                chunk_idx = d.metadata.get("chunk_index") if d.metadata.get("chunk_index") is not None else -1
                key = (doc_id, chunk_idx, d.page_content[:128])
                if key not in seen_keys:
                    seen_keys.add(key)
                    combined_docs.append(d)

        docs = combined_docs
        
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
            query=augmented_question,
            documents=docs,
            top_k=k,
            confidence_threshold=confidence_threshold,
        )
        
        if not reranked_results:
            clarifier = _build_clarifying_question(question, expansions, docs)
            return {
                "response": clarifier,
                "success": True,
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

        # Include neighbor chunks (±1) for top results when available in combined_docs
        context_docs: List[Document] = list(reranked_docs)
        try:
            # Build quick index for combined docs by (document_id, chunk_index)
            combined_index = {}
            for d in docs:
                did = d.metadata.get("document_id") or d.metadata.get("doc_id") or d.metadata.get("source") or ""
                cidx = d.metadata.get("chunk_index") if d.metadata.get("chunk_index") is not None else -1
                combined_index[(did, cidx)] = d

            # For top N reranked docs, add neighbors if present
            TOP_N_FOR_NEIGHBORS = min(2, len(reranked_docs))
            added_keys = set()
            for top_doc in reranked_docs[:TOP_N_FOR_NEIGHBORS]:
                did = top_doc.metadata.get("document_id") or top_doc.metadata.get("doc_id") or top_doc.metadata.get("source") or ""
                cidx = top_doc.metadata.get("chunk_index") if top_doc.metadata.get("chunk_index") is not None else -1
                for neighbor_idx in (cidx - 1, cidx + 1):
                    key = (did, neighbor_idx)
                    if key in combined_index:
                        neighbor_doc = combined_index[key]
                        if neighbor_doc not in context_docs and key not in added_keys:
                            context_docs.append(neighbor_doc)
                            added_keys.add(key)
        except Exception:
            # Best-effort; ignore neighbor augmentation failures
            context_docs = list(reranked_docs)
        
        # Calculate overall confidence
        overall_confidence = sum(result["confidence"] for result in reranked_results) / len(reranked_results)
        
        # Build enhanced prompt with augmented context
        metaprompt = build_metaprompt(question, context_docs, sources)
        
        # Generate response
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        llm_response = llm.invoke(metaprompt)
        response_text = llm_response.content
        
        # Add source citations (disabled for user-facing output)
        citations = guardrails.format_source_citations(sources)
        response_with_citations = response_text
        
        # Sanitize response
        sanitized_response = guardrails.sanitize_response(response_with_citations)
        
        # Validate response
        response_valid, validation_msg = guardrails.validate_response(
            sanitized_response, overall_confidence, sources
        )
        
        if not response_valid:
            # Provide clarifying question instead of blocking on low confidence
            if "confidence" in validation_msg.lower():
                clarifier = _build_clarifying_question(question, expansions, docs)
                return {
                    "response": clarifier,
                    "success": True,
                    "response_id": response_id,
                    "confidence_score": overall_confidence,
                    "sources": sources
                }
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
