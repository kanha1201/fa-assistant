"""Minimal database using SQLite only."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4
from src.utils.logger_minimal import logger


class MinimalDatabase:
    """Minimal database using SQLite."""
    
    def __init__(self, db_path: str = "./data/financial_data.db"):
        """Initialize database."""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        self.logger = logger
    
    def _create_tables(self):
        """Create database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id TEXT PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT,
                sector TEXT,
                industry TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Financial metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_metrics (
                id TEXT PRIMARY KEY,
                company_id TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                period_type TEXT,
                period_date TEXT,
                source TEXT,
                metadata TEXT,
                created_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                company_id TEXT,
                document_type TEXT,
                source_url TEXT,
                content_text TEXT,
                metadata TEXT,
                embedding_id TEXT,
                file_path TEXT,
                created_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_session(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_or_create_company(self, symbol: str, name: Optional[str] = None,
                              sector: Optional[str] = None) -> Dict:
        """Get or create company."""
        conn = self.get_session()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT id, name, sector FROM companies WHERE symbol = ?", (symbol.upper(),))
        row = cursor.fetchone()
        
        if row:
            company = {"id": row[0], "symbol": symbol.upper(), "name": row[1], "sector": row[2]}
        else:
            company_id = str(uuid4())
            cursor.execute("""
                INSERT INTO companies (id, symbol, name, sector, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, symbol.upper(), name, sector, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            company = {"id": company_id, "symbol": symbol.upper(), "name": name, "sector": sector}
        
        conn.close()
        return company
    
    def save_document(self, company_id: Optional[str], document_type: str,
                     source_url: str, content_text: str, metadata: Optional[dict] = None,
                     file_path: Optional[str] = None) -> Dict:
        """Save document."""
        conn = self.get_session()
        cursor = conn.cursor()
        
        doc_id = str(uuid4())
        cursor.execute("""
            INSERT INTO documents (id, company_id, document_type, source_url, content_text, metadata, file_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, company_id, document_type, source_url, content_text,
            json.dumps(metadata or {}), file_path, datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return {"id": doc_id, "company_id": company_id, "document_type": document_type}


db = MinimalDatabase()


