# rag/metadata_db.py

import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class MetadataDB:
    def __init__(self, db_path: str = "data/metadata.db", enabled: bool = True):
        """
        Initialize metadata database for tracking queries, sources, and usage.
        
        Args:
            db_path: Path to SQLite database file
            enabled: Whether to enable database functionality
        """
        self.db_path = db_path
        self.enabled = enabled
        
        if self.enabled:
            self._ensure_db_directory()
            self._create_tables()
        else:
            print("📝 Metadata database disabled - analytics will not be tracked")
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    user_id TEXT,
                    client_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    response_length INTEGER,
                    sources_used TEXT,
                    processing_time_ms INTEGER
                )
            """)
            
            # Source citations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_citations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id INTEGER,
                    source_name TEXT NOT NULL,
                    source_type TEXT,
                    doc_id TEXT,
                    confidence_score REAL,
                    rank_position INTEGER,
                    FOREIGN KEY (query_id) REFERENCES query_history (id)
                )
            """)
            
            # Usage analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_queries INTEGER DEFAULT 0,
                    successful_queries INTEGER DEFAULT 0,
                    failed_queries INTEGER DEFAULT 0,
                    avg_confidence_score REAL DEFAULT 0,
                    avg_response_time_ms REAL DEFAULT 0
                )
            """)
            
            # Tool usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id INTEGER,
                    tool_name TEXT NOT NULL,
                    tool_category TEXT,
                    usage_count INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_id) REFERENCES query_history (id)
                )
            """)
            
            conn.commit()
    
    def log_query(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        client_type: str = "web",
        confidence_score: Optional[float] = None,
        response_length: Optional[int] = None,
        sources_used: Optional[List[Dict]] = None,
        processing_time_ms: Optional[int] = None
    ) -> int:
        """
        Log a query to the database.
        
        Args:
            query_text: The user's query
            user_id: Optional user identifier
            client_type: Type of client (web, telegram, etc.)
            confidence_score: Overall confidence score
            response_length: Length of the response
            sources_used: List of sources used in response
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Query ID for reference
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO query_history 
                (query_text, user_id, client_type, confidence_score, response_length, sources_used, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                query_text,
                user_id,
                client_type,
                confidence_score,
                response_length,
                json.dumps(sources_used) if sources_used else None,
                processing_time_ms
            ))
            
            query_id = cursor.lastrowid
            
            # Log source citations if provided
            if sources_used:
                for source in sources_used:
                    cursor.execute("""
                        INSERT INTO source_citations 
                        (query_id, source_name, source_type, doc_id, confidence_score, rank_position)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        query_id,
                        source.get("source", "Unknown"),
                        source.get("source_type", "Unknown"),
                        source.get("doc_id", "Unknown"),
                        source.get("confidence", 0.0),
                        source.get("rank", 0)
                    ))
            
            conn.commit()
            return query_id
    
    def log_tool_usage(
        self,
        query_id: int,
        tool_name: str,
        tool_category: str = "general"
    ):
        """
        Log tool usage for a query.
        
        Args:
            query_id: ID of the query
            tool_name: Name of the tool used
            tool_category: Category of the tool
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tool_usage (query_id, tool_name, tool_category)
                VALUES (?, ?, ?)
            """, (query_id, tool_name, tool_category))
            
            conn.commit()
    
    def get_query_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get query history for a user or all users.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of query history records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT * FROM query_history 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                """, (user_id, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM query_history 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_source_citations(self, query_id: int) -> List[Dict]:
        """
        Get source citations for a specific query.
        
        Args:
            query_id: ID of the query
            
        Returns:
            List of source citations
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM source_citations 
                WHERE query_id = ? 
                ORDER BY rank_position ASC
            """, (query_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_usage_analytics(self, days: int = 30) -> Dict:
        """
        Get usage analytics for the specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get daily stats
            cursor.execute("""
                SELECT 
                    date,
                    total_queries,
                    successful_queries,
                    failed_queries,
                    avg_confidence_score,
                    avg_response_time_ms
                FROM usage_analytics 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days))
            
            daily_stats = cursor.fetchall()
            
            # Get top sources
            cursor.execute("""
                SELECT 
                    source_name,
                    COUNT(*) as usage_count,
                    AVG(confidence_score) as avg_confidence
                FROM source_citations 
                WHERE query_id IN (
                    SELECT id FROM query_history 
                    WHERE timestamp >= datetime('now', '-{} days')
                )
                GROUP BY source_name 
                ORDER BY usage_count DESC 
                LIMIT 10
            """.format(days))
            
            top_sources = cursor.fetchall()
            
            # Get tool usage
            cursor.execute("""
                SELECT 
                    tool_name,
                    tool_category,
                    COUNT(*) as usage_count
                FROM tool_usage 
                WHERE query_id IN (
                    SELECT id FROM query_history 
                    WHERE timestamp >= datetime('now', '-{} days')
                )
                GROUP BY tool_name, tool_category 
                ORDER BY usage_count DESC
            """.format(days))
            
            tool_usage = cursor.fetchall()
            
            return {
                "daily_stats": daily_stats,
                "top_sources": top_sources,
                "tool_usage": tool_usage
            }
    
    def update_daily_analytics(self):
        """Update daily analytics summary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get today's stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(CASE WHEN confidence_score >= 0.5 THEN 1 END) as successful_queries,
                    COUNT(CASE WHEN confidence_score < 0.5 THEN 1 END) as failed_queries,
                    AVG(confidence_score) as avg_confidence_score,
                    AVG(processing_time_ms) as avg_response_time_ms
                FROM query_history 
                WHERE DATE(timestamp) = DATE('now')
            """)
            
            stats = cursor.fetchone()
            
            if stats[0] > 0:  # Only update if there are queries today
                cursor.execute("""
                    INSERT OR REPLACE INTO usage_analytics 
                    (date, total_queries, successful_queries, failed_queries, avg_confidence_score, avg_response_time_ms)
                    VALUES (DATE('now'), ?, ?, ?, ?, ?)
                """, stats)
                
                conn.commit()

# Global database instance
_metadata_db = None

def get_metadata_db() -> MetadataDB:
    """Get or create global metadata database instance."""
    global _metadata_db
    if _metadata_db is None:
        _metadata_db = MetadataDB()
    return _metadata_db 