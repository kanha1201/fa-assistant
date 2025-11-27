"""RAG (Retrieval-Augmented Generation) pipeline."""
from typing import List, Dict, Optional
from src.storage import vector_store, db
from src.utils import logger


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for financial data."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_store = vector_store
        self.logger = logger
    
    def retrieve_context(self, query: str, company_symbol: Optional[str] = None,
                        document_types: Optional[List[str]] = None,
                        n_results: int = 5) -> List[Dict]:
        """Retrieve relevant context from vector store.
        
        Args:
            query: Search query
            company_symbol: Filter by company symbol
            document_types: Filter by document types
            n_results: Number of results to retrieve
        
        Returns:
            List of context documents with metadata
        """
        try:
            # Build metadata filter
            where = {}
            if company_symbol:
                where["company_symbol"] = company_symbol
            if document_types:
                where["document_type"] = {"$in": document_types}
            
            # Query vector store
            results = self.vector_store.query(
                query_text=query,
                n_results=n_results,
                filter_metadata=where if where else None
            )
            
            # Format results
            contexts = []
            if results and "documents" in results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    contexts.append({
                        "text": doc,
                        "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                        "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None
                    })
            
            self.logger.debug(f"Retrieved {len(contexts)} context documents for query: {query[:50]}...")
            return contexts
        
        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}", exc_info=True)
            return []
    
    def get_company_metrics(self, company_symbol: str) -> Dict:
        """Get structured financial metrics for a company.
        
        Args:
            company_symbol: Company symbol
        
        Returns:
            Dictionary of metrics
        """
        try:
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(symbol=company_symbol.upper()).first()
                if not company:
                    return {}
                
                metrics = {}
                financial_metrics = session.query(db.FinancialMetric).filter_by(
                    company_id=company.id
                ).all()
                
                for metric in financial_metrics:
                    metrics[metric.metric_name] = {
                        "value": float(metric.metric_value) if metric.metric_value else None,
                        "period_type": metric.period_type,
                        "source": metric.source
                    }
                
                return metrics
            finally:
                session.close()
        
        except Exception as e:
            self.logger.error(f"Error getting company metrics: {e}", exc_info=True)
            return {}
    
    def get_sector_benchmarks(self, sector: str, metric_name: Optional[str] = None) -> Dict:
        """Get sector benchmarks.
        
        Args:
            sector: Sector name
            metric_name: Optional specific metric
        
        Returns:
            Dictionary of benchmarks
        """
        try:
            session = db.get_session()
            try:
                query = session.query(db.SectorBenchmark).filter_by(sector=sector)
                if metric_name:
                    query = query.filter_by(metric_name=metric_name)
                
                benchmarks = query.all()
                
                result = {}
                for bench in benchmarks:
                    result[bench.metric_name] = {
                        "benchmark_value": float(bench.benchmark_value) if bench.benchmark_value else None,
                        "percentile_25": float(bench.percentile_25) if bench.percentile_25 else None,
                        "percentile_50": float(bench.percentile_50) if bench.percentile_50 else None,
                        "percentile_75": float(bench.percentile_75) if bench.percentile_75 else None,
                    }
                
                return result
            finally:
                session.close()
        
        except Exception as e:
            self.logger.error(f"Error getting sector benchmarks: {e}", exc_info=True)
            return {}
    
    def get_company_context(self, company_symbol: str, query: str, 
                           n_results: int = 5) -> Dict:
        """Get comprehensive context for a company query.
        
        Args:
            company_symbol: Company symbol
            query: User query
            n_results: Number of context documents
        
        Returns:
            Dictionary with context text, metrics, and metadata
        """
        # Retrieve relevant documents
        contexts = self.retrieve_context(
            query=query,
            company_symbol=company_symbol,
            n_results=n_results
        )
        
        # Get structured metrics
        metrics = self.get_company_metrics(company_symbol)
        
        # Combine context text
        context_texts = [ctx["text"] for ctx in contexts]
        
        return {
            "context_texts": context_texts,
            "contexts": contexts,
            "metrics": metrics,
            "company_symbol": company_symbol
        }


