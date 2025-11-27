"""Vector database for RAG pipeline using ChromaDB."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
from src.utils import logger, settings


class VectorStore:
    """Vector database for storing document embeddings."""
    
    def __init__(self):
        """Initialize vector store."""
        self.logger = logger
        self.persist_directory = Path(settings.vector_db_path)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection_name = "financial_documents"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Financial documents for RAG pipeline"}
            )
            self.logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict], ids: Optional[List[str]] = None):
        """Add documents to vector store.
        
        Args:
            texts: List of text documents
            metadatas: List of metadata dictionaries for each document
            ids: Optional list of document IDs
        """
        if not ids:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if len(texts) != len(metadatas) or len(texts) != len(ids):
            raise ValueError("texts, metadatas, and ids must have the same length")
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        self.logger.info(f"Added {len(texts)} documents to vector store")
        return ids
    
    def query(self, query_text: str, n_results: int = 5, 
              filter_metadata: Optional[Dict] = None) -> Dict:
        """Query the vector store.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
        
        Returns:
            Dictionary with ids, documents, distances, and metadatas
        """
        where = filter_metadata if filter_metadata else None
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_by_ids(self, ids: List[str]) -> Dict:
        """Get documents by their IDs."""
        return self.collection.get(ids=ids)
    
    def delete(self, ids: List[str]):
        """Delete documents by IDs."""
        self.collection.delete(ids=ids)
        self.logger.info(f"Deleted {len(ids)} documents from vector store")
    
    def count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count()


# Initialize vector store
vector_store = VectorStore()


