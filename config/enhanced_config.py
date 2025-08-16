# config/enhanced_config.py

import os
from typing import Dict, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EmbeddingConfig:
    """Configuration for embeddings."""
    model: str = "text-embedding-3-large"
    dimensions: int = 3072
    chunk_size: int = 800
    chunk_overlap: int = 100

@dataclass
class RerankingConfig:
    """Configuration for reranking."""
    model: str = "BAAI/bge-reranker-base"
    confidence_threshold: float = 0.5
    max_documents: int = 8
    top_k: int = 4

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
    
    def __post_init__(self):
        if self.restricted_keywords is None:
            self.restricted_keywords = [
                "password", "api_key", "secret", "private", "confidential",
                "financial_advice", "investment_advice", "legal_advice"
            ]

@dataclass
class DatabaseConfig:
    """Configuration for databases."""
    qdrant_url: str = None
    qdrant_api_key: str = None
    qdrant_collection: str = "layerzero-rag"
    metadata_db_path: str = "data/metadata.db"
    
    def __post_init__(self):
        self.qdrant_url = self.qdrant_url or os.getenv("QDRANT_URL")
        self.qdrant_api_key = self.qdrant_api_key or os.getenv("QDRANT_API_KEY")

@dataclass
class LLMConfig:
    """Configuration for language models."""
    model: str = "gpt-4o"
    temperature: float = 0.0
    max_tokens: int = 2000

@dataclass
class APIConfig:
    """Configuration for API keys."""
    openai_api_key: str = None
    telegram_bot_token: str = None
    
    def __post_init__(self):
        self.openai_api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.telegram_bot_token = self.telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN")

@dataclass
class EnhancedConfig:
    """Main configuration class."""
    embedding: EmbeddingConfig = None
    reranking: RerankingConfig = None
    guardrails: GuardrailConfig = None
    database: DatabaseConfig = None
    llm: LLMConfig = None
    api: APIConfig = None
    
    def __post_init__(self):
        if self.embedding is None:
            self.embedding = EmbeddingConfig()
        if self.reranking is None:
            self.reranking = RerankingConfig()
        if self.guardrails is None:
            self.guardrails = GuardrailConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.llm is None:
            self.llm = LLMConfig()
        if self.api is None:
            self.api = APIConfig()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Check required API keys
        if not self.api.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if not self.api.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        # Check database configuration
        if not self.database.qdrant_url:
            errors.append("QDRANT_URL is required")
        
        if not self.database.qdrant_api_key:
            errors.append("QDRANT_API_KEY is required")
        
        return errors
    
    def get_summary(self) -> Dict:
        """Get a summary of the configuration."""
        return {
            "embedding_model": self.embedding.model,
            "reranking_model": self.reranking.model,
            "confidence_threshold": self.guardrails.min_confidence_threshold,
            "rate_limiting": {
                "per_minute": self.guardrails.rate_limit_queries_per_minute,
                "per_hour": self.guardrails.rate_limit_queries_per_hour
            },
            "llm_model": self.llm.model,
            "database": {
                "qdrant_collection": self.database.qdrant_collection,
                "metadata_db": self.database.metadata_db_path
            }
        }

# Global configuration instance
_config = None

def get_config() -> EnhancedConfig:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = EnhancedConfig()
    return _config

def validate_config() -> bool:
    """Validate the configuration and return True if valid."""
    config = get_config()
    errors = config.validate()
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration is valid")
    return True

def print_config_summary():
    """Print a summary of the current configuration."""
    config = get_config()
    summary = config.get_summary()
    
    print("🔧 Configuration Summary:")
    print(f"  Embedding Model: {summary['embedding_model']}")
    print(f"  Reranking Model: {summary['reranking_model']}")
    print(f"  Confidence Threshold: {summary['confidence_threshold']}")
    print(f"  Rate Limiting: {summary['rate_limiting']['per_minute']}/min, {summary['rate_limiting']['per_hour']}/hour")
    print(f"  LLM Model: {summary['llm_model']}")
    print(f"  Qdrant Collection: {summary['database']['qdrant_collection']}")
    print(f"  Metadata DB: {summary['database']['metadata_db']}")

if __name__ == "__main__":
    print_config_summary()
    validate_config() 