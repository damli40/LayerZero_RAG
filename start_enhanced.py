#!/usr/bin/env python3
# start_enhanced.py

import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "openai", "langchain", "qdrant_client",
        "sentence_transformers", "torch", "transformers", "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_environment():
    """Check environment variables and configuration."""
    print("\n🔧 Checking environment configuration...")
    
    from config.enhanced_config import validate_config, print_config_summary
    
    print_config_summary()
    
    if not validate_config():
        print("\n❌ Configuration validation failed")
        print("Please check your .env file and ensure all required variables are set")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def initialize_database():
    """Initialize the metadata database."""
    print("\n🗄️ Initializing metadata database...")
    
    try:
        from rag.metadata_db import get_metadata_db
        db = get_metadata_db()
        print("✅ Metadata database initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize metadata database: {e}")
        return False

def test_components():
    """Test core components."""
    print("\n🧪 Testing core components...")
    
    try:
        # Test guardrails
        from rag.guardrails import get_guardrails
        guardrails = get_guardrails()
        print("  ✅ Guardrails initialized")
        
        # Test reranker (this will download the model)
        print("  📥 Downloading reranker model (this may take a moment)...")
        from rag.rerank import get_reranker
        reranker = get_reranker()
        print("  ✅ Reranker initialized")
        
        # Test configuration
        from config.enhanced_config import get_config
        config = get_config()
        print("  ✅ Configuration loaded")
        
        print("✅ All core components are working")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "data",
        "data/docs",
        "data/LayerZero_primitives",
        "data/thread_templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ All directories created")

def print_startup_info():
    """Print startup information."""
    print("\n" + "="*60)
    print("🚀 ENHANCED OMNICHAIN ASSISTANT STARTUP")
    print("="*60)
    print()
    print("✨ New Features Added:")
    print("  • text-embedding-3-large for better embeddings")
    print("  • BGE reranker for improved search relevance")
    print("  • SQLite metadata database for tracking")
    print("  • Comprehensive guardrails system")
    print("  • Source citation requirements")
    print("  • Confidence scoring and thresholds")
    print("  • Rate limiting and content safety")
    print("  • Tool restriction by prompt category")
    print()
    print("🔧 System Components:")
    print("  • Ingestion → Preprocess → Vector DB (Qdrant)")
    print("  • Reranking → Orchestrator (FastAPI)")
    print("  • Skills → Clients (Web UI, Telegram)")
    print("  • Metadata DB (SQLite) for analytics")
    print()
    print("🛡️ Guardrails Active:")
    print("  • Source citation required")
    print("  • Confidence score threshold: 0.5")
    print("  • Rate limits: 10/min, 100/hour")
    print("  • Content safety checks")
    print("  • Tool restrictions by category")
    print()

def main():
    """Main startup function."""
    print_startup_info()
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", initialize_database),
        ("Components", test_components),
        ("Directories", create_directories)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        if not check_func():
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n❌ Startup failed. Failed checks: {', '.join(failed_checks)}")
        print("Please fix the issues above and try again.")
        return False
    
    print("\n" + "="*60)
    print("✅ ENHANCED SYSTEM READY!")
    print("="*60)
    print()
    print("🚀 To start the system:")
    print("  • Web UI: uvicorn app.main:app --reload")
    print("  • Telegram Bot: python bot/bot.py")
    print("  • Ingest Data: python rag/ingest.py")
    print()
    print("📊 Analytics available at: /analytics")
    print("🏥 Health check at: /health")
    print()
    print("🎉 Enhanced Omnichain Assistant is ready to use!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 