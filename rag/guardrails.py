# rag/guardrails.py

import re
import time
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

class PromptCategory(Enum):
    """Categories for different types of prompts."""
    GENERAL_QUERY = "general_query"
    TECHNICAL_DETAILS = "technical_details"
    CONTENT_GENERATION = "content_generation"
    ANALYTICS = "analytics"
    ADMIN = "admin"

class ToolCategory(Enum):
    """Categories for different tools."""
    RAG_QUERY = "rag_query"
    CONTENT_GENERATION = "content_generation"
    ANALYTICS = "analytics"
    ADMIN = "admin"

@dataclass
class GuardrailConfig:
    """Configuration for guardrails."""
    min_confidence_threshold: float = 0.5
    max_response_length: int = 2000
    rate_limit_queries_per_minute: int = 10
    rate_limit_queries_per_hour: int = 100
    require_source_citation: bool = True
    max_sources_per_response: int = 5
    restricted_keywords: List[str] = None
    allowed_tools_by_category: Dict[PromptCategory, List[ToolCategory]] = None
    
    def __post_init__(self):
        if self.restricted_keywords is None:
            self.restricted_keywords = [
                "password", "api_key", "secret", "private", "confidential",
                "financial_advice", "investment_advice", "legal_advice"
            ]
        
        if self.allowed_tools_by_category is None:
            self.allowed_tools_by_category = {
                PromptCategory.GENERAL_QUERY: [ToolCategory.RAG_QUERY],
                PromptCategory.TECHNICAL_DETAILS: [ToolCategory.RAG_QUERY, ToolCategory.ANALYTICS],
                PromptCategory.CONTENT_GENERATION: [ToolCategory.RAG_QUERY, ToolCategory.CONTENT_GENERATION],
                PromptCategory.ANALYTICS: [ToolCategory.ANALYTICS],
                PromptCategory.ADMIN: [ToolCategory.ADMIN, ToolCategory.ANALYTICS]
            }

class Guardrails:
    def __init__(self, config: Optional[GuardrailConfig] = None):
        """
        Initialize guardrails system.
        
        Args:
            config: Guardrail configuration
        """
        self.config = config or GuardrailConfig()
        self.rate_limit_cache = {}  # Simple in-memory rate limiting
        self.user_queries = {}  # Track user query history
    
    def classify_prompt(self, query: str) -> PromptCategory:
        """
        Classify the type of prompt based on content.
        
        Args:
            query: User query text
            
        Returns:
            PromptCategory classification
        """
        query_lower = query.lower()
        
        # Content generation keywords
        if any(word in query_lower for word in ["generate", "create", "write", "thread", "content", "post"]):
            return PromptCategory.CONTENT_GENERATION
        
        # Technical details keywords
        if any(word in query_lower for word in ["how", "what is", "explain", "technical", "implementation", "code"]):
            return PromptCategory.TECHNICAL_DETAILS
        
        # Analytics keywords
        if any(word in query_lower for word in ["analytics", "stats", "usage", "metrics", "performance"]):
            return PromptCategory.ANALYTICS
        
        # Admin keywords
        if any(word in query_lower for word in ["admin", "system", "config", "settings"]):
            return PromptCategory.ADMIN
        
        return PromptCategory.GENERAL_QUERY
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (allowed, message)
        """
        now = datetime.utcnow()
        
        if user_id not in self.rate_limit_cache:
            self.rate_limit_cache[user_id] = []
        
        # Clean old entries
        self.rate_limit_cache[user_id] = [
            timestamp for timestamp in self.rate_limit_cache[user_id]
            if now - timestamp < timedelta(hours=1)
        ]
        
        # Check hourly limit
        if len(self.rate_limit_cache[user_id]) >= self.config.rate_limit_queries_per_hour:
            return False, f"Hourly rate limit exceeded ({self.config.rate_limit_queries_per_hour} queries)"
        
        # Check minute limit (last 60 seconds)
        recent_queries = [
            timestamp for timestamp in self.rate_limit_cache[user_id]
            if now - timestamp < timedelta(minutes=1)
        ]
        
        if len(recent_queries) >= self.config.rate_limit_queries_per_minute:
            return False, f"Minute rate limit exceeded ({self.config.rate_limit_queries_per_minute} queries)"
        
        # Add current query
        self.rate_limit_cache[user_id].append(now)
        return True, "Rate limit check passed"
    
    def check_content_safety(self, query: str) -> Tuple[bool, str]:
        """
        Check if query contains restricted content.
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (safe, message)
        """
        query_lower = query.lower()
        
        # Check for restricted keywords
        for keyword in self.config.restricted_keywords:
            if keyword in query_lower:
                return False, f"Query contains restricted keyword: {keyword}"
        
        # Check for potential injection attempts
        injection_patterns = [
            r"<script.*?>",
            r"javascript:",
            r"on\w+\s*=",
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False, f"Query contains potentially unsafe content"
        
        return True, "Content safety check passed"
    
    def validate_tool_access(
        self, 
        prompt_category: PromptCategory, 
        requested_tools: List[ToolCategory]
    ) -> Tuple[bool, List[ToolCategory]]:
        """
        Validate if tools can be used for the given prompt category.
        
        Args:
            prompt_category: Category of the prompt
            requested_tools: List of tools requested
            
        Returns:
            Tuple of (allowed, allowed_tools)
        """
        allowed_tools = self.config.allowed_tools_by_category.get(prompt_category, [])
        
        # Check if all requested tools are allowed
        unauthorized_tools = [tool for tool in requested_tools if tool not in allowed_tools]
        
        if unauthorized_tools:
            return False, allowed_tools
        
        return True, requested_tools
    
    def format_source_citations(self, sources: List[Dict]) -> str:
        """
        Format source citations for inclusion in response.
        
        Args:
            sources: List of source dictionaries with metadata
            
        Returns:
            Formatted citation string
        """
        if not sources:
            return ""
        
        citations = []
        for i, source in enumerate(sources[:self.config.max_sources_per_response], 1):
            source_name = source.get("source", "Unknown")
            confidence = source.get("confidence", 0.0)
            source_type = source.get("source_type", "Unknown")
            
            citation = f"{i}. {source_name} ({source_type}, confidence: {confidence:.2f})"
            citations.append(citation)
        
        return "\n\n**Sources:**\n" + "\n".join(citations)
    
    def validate_response(
        self, 
        response: str, 
        confidence_score: float, 
        sources: List[Dict]
    ) -> Tuple[bool, str]:
        """
        Validate response meets guardrail requirements.
        
        Args:
            response: Generated response
            confidence_score: Confidence score of response
            sources: Sources used in response
            
        Returns:
            Tuple of (valid, message)
        """
        # Check confidence threshold
        if confidence_score < self.config.min_confidence_threshold:
            return False, f"Response confidence ({confidence_score:.2f}) below threshold ({self.config.min_confidence_threshold})"
        
        # Check response length
        if len(response) > self.config.max_response_length:
            return False, f"Response length ({len(response)}) exceeds limit ({self.config.max_response_length})"
        
        # Check source citation requirement
        if self.config.require_source_citation and not sources:
            return False, "Source citation required but no sources provided"
        
        return True, "Response validation passed"
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response to remove potentially harmful content.
        
        Args:
            response: Raw response text
            
        Returns:
            Sanitized response
        """
        # Remove HTML tags
        response = re.sub(r'<[^>]+>', '', response)
        
        # Remove script tags and content
        response = re.sub(r'<script.*?</script>', '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove potentially dangerous URLs
        response = re.sub(r'javascript:', '', response, flags=re.IGNORECASE)
        
        # Limit response length
        if len(response) > self.config.max_response_length:
            response = response[:self.config.max_response_length] + "..."
        
        return response
    
    def generate_response_id(self, query: str, user_id: str) -> str:
        """
        Generate a unique response ID for tracking.
        
        Args:
            query: User query
            user_id: User identifier
            
        Returns:
            Unique response ID
        """
        timestamp = datetime.utcnow().isoformat()
        content = f"{user_id}:{query}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_allowed_tools_for_prompt(self, query: str) -> List[ToolCategory]:
        """
        Get allowed tools for a given prompt.
        
        Args:
            query: User query
            
        Returns:
            List of allowed tool categories
        """
        prompt_category = self.classify_prompt(query)
        return self.config.allowed_tools_by_category.get(prompt_category, [])

# Global guardrails instance
_guardrails = None

def get_guardrails() -> Guardrails:
    """Get or create global guardrails instance."""
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails 