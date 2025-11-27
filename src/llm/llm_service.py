"""LLM service for financial analysis features."""
from typing import Dict, List, Optional
from src.llm.gemini_client import GeminiClient
from src.llm.rag_pipeline import RAGPipeline
from src.llm.prompts import PromptTemplates
from src.llm.guardrails import guardrails
from src.storage import db
from src.utils import logger, settings


class LLMService:
    """Service for LLM-powered financial analysis."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.gemini_client = GeminiClient()
        self.rag_pipeline = RAGPipeline()
        self.prompts = PromptTemplates()
        self.logger = logger
    
    def get_quarterly_summary(self, company_symbol: str) -> Dict:
        """Generate quarterly summary.
        
        Args:
            company_symbol: Company symbol
        
        Returns:
            Dictionary with summary text
        """
        try:
            # Get company info
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(
                    symbol=company_symbol.upper()
                ).first()
                if not company:
                    return {"error": f"Company {company_symbol} not found"}
                
                company_name = company.name or company_symbol
                sector = company.sector or "Unknown"
            finally:
                session.close()
            
            # Get context
            context_data = self.rag_pipeline.get_company_context(
                company_symbol=company_symbol,
                query="quarterly results financial performance",
                n_results=5
            )
            
            # Generate prompt
            prompt = self.prompts.quarterly_summary_prompt(
                company_name=company_name,
                context=context_data["context_texts"]
            )
            
            # Generate response
            summary = self.gemini_client.generate(
                prompt=prompt,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens
            )
            
            return {
                "summary": summary.strip(),
                "company_symbol": company_symbol,
                "company_name": company_name
            }
        
        except Exception as e:
            self.logger.error(f"Error generating quarterly summary: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_bull_bear_case(self, company_symbol: str) -> Dict:
        """Generate bull vs bear case.
        
        Args:
            company_symbol: Company symbol
        
        Returns:
            Dictionary with bull and bear cases
        """
        try:
            # Get company info
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(
                    symbol=company_symbol.upper()
                ).first()
                if not company:
                    return {"error": f"Company {company_symbol} not found"}
                
                company_name = company.name or company_symbol
                sector = company.sector or "Unknown"
            finally:
                session.close()
            
            # Get context and metrics
            context_data = self.rag_pipeline.get_company_context(
                company_symbol=company_symbol,
                query="bull case bear case strengths weaknesses risks opportunities",
                n_results=8
            )
            
            # Generate prompt
            prompt = self.prompts.bull_bear_case_prompt(
                company_name=company_name,
                sector=sector,
                context=context_data["context_texts"],
                metrics=context_data["metrics"]
            )
            
            # Generate response
            response = self.gemini_client.generate(
                prompt=prompt,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens
            )
            
            # Apply guardrails
            response = guardrails.ensure_neutral_tone(response)
            response = guardrails.add_disclaimer(response, "bull_bear")
            
            # Parse bull and bear cases (simple parsing)
            bull_case = []
            bear_case = []
            current_section = None
            
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                
                if "BULL" in line.upper() or "BULLISH" in line.upper():
                    current_section = "bull"
                elif "BEAR" in line.upper() or "BEARISH" in line.upper():
                    current_section = "bear"
                elif line.startswith("-") or line.startswith("•"):
                    point = line.lstrip("- •").strip()
                    if current_section == "bull":
                        bull_case.append(point)
                    elif current_section == "bear":
                        bear_case.append(point)
            
            return {
                "bull_case": bull_case if bull_case else [response],
                "bear_case": bear_case if bear_case else [],
                "full_response": response,
                "company_symbol": company_symbol,
                "company_name": company_name
            }
        
        except Exception as e:
            self.logger.error(f"Error generating bull/bear case: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_red_flags(self, company_symbol: str) -> Dict:
        """Generate red flags analysis.
        
        Args:
            company_symbol: Company symbol
        
        Returns:
            Dictionary with red flags
        """
        try:
            # Get company info
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(
                    symbol=company_symbol.upper()
                ).first()
                if not company:
                    return {"error": f"Company {company_symbol} not found"}
                
                company_name = company.name or company_symbol
                sector = company.sector or "Unknown"
            finally:
                session.close()
            
            # Get context, metrics, and benchmarks
            context_data = self.rag_pipeline.get_company_context(
                company_symbol=company_symbol,
                query="red flags risks concerns problems issues",
                n_results=8
            )
            
            benchmarks = {}
            if sector and sector != "Unknown":
                benchmarks = self.rag_pipeline.get_sector_benchmarks(sector)
            
            # Generate prompt
            prompt = self.prompts.red_flags_prompt(
                company_name=company_name,
                sector=sector,
                context=context_data["context_texts"],
                metrics=context_data["metrics"],
                benchmarks=benchmarks if benchmarks else None
            )
            
            # Generate response
            response = self.gemini_client.generate(
                prompt=prompt,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens
            )
            
            # Apply guardrails
            response = guardrails.ensure_neutral_tone(response)
            response = guardrails.add_disclaimer(response, "red_flags")
            
            # Parse red flags
            red_flags = []
            current_flag = {}
            
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    if current_flag:
                        red_flags.append(current_flag)
                        current_flag = {}
                    continue
                
                if line.startswith(("High:", "Medium:", "Low:")) or "Severity:" in line:
                    if "High" in line:
                        current_flag["severity"] = "High"
                    elif "Medium" in line:
                        current_flag["severity"] = "Medium"
                    elif "Low" in line:
                        current_flag["severity"] = "Low"
                elif line.startswith(("-", "•", "1.", "2.", "3.")):
                    if current_flag:
                        red_flags.append(current_flag)
                    current_flag = {"description": line.lstrip("- •1234567890.").strip()}
                elif current_flag:
                    if "description" in current_flag:
                        current_flag["description"] += " " + line
            
            if current_flag:
                red_flags.append(current_flag)
            
            return {
                "red_flags": red_flags if red_flags else [{"description": response, "severity": "Unknown"}],
                "full_response": response,
                "company_symbol": company_symbol,
                "company_name": company_name
            }
        
        except Exception as e:
            self.logger.error(f"Error generating red flags: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_benchmark(self, company_symbol: str, metric_name: str) -> Dict:
        """Generate benchmark comparison.
        
        Args:
            company_symbol: Company symbol
            metric_name: Metric name to benchmark
        
        Returns:
            Dictionary with benchmark comparison
        """
        try:
            # Get company info
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(
                    symbol=company_symbol.upper()
                ).first()
                if not company:
                    return {"error": f"Company {company_symbol} not found"}
                
                company_name = company.name or company_symbol
                sector = company.sector or "Unknown"
            finally:
                session.close()
            
            # Get company metric value
            metrics = self.rag_pipeline.get_company_metrics(company_symbol)
            company_value = None
            if metric_name in metrics:
                company_value = metrics[metric_name].get("value")
            
            # Get sector benchmarks
            benchmarks = {}
            if sector and sector != "Unknown":
                benchmarks = self.rag_pipeline.get_sector_benchmarks(sector, metric_name)
            
            if not benchmarks:
                return {
                    "error": f"Benchmark data not available for {metric_name} in {sector} sector"
                }
            
            # Generate prompt
            prompt = self.prompts.benchmark_prompt(
                company_name=company_name,
                metric_name=metric_name,
                company_value=company_value,
                sector=sector,
                benchmarks=benchmarks
            )
            
            # Generate response
            comparison = self.gemini_client.generate(
                prompt=prompt,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens
            )
            
            # Apply guardrails
            comparison = guardrails.ensure_neutral_tone(comparison)
            comparison = guardrails.add_disclaimer(comparison, "benchmark")
            
            return {
                "comparison": comparison.strip(),
                "company_symbol": company_symbol,
                "company_name": company_name,
                "metric_name": metric_name,
                "company_value": company_value,
                "sector": sector,
                "benchmarks": benchmarks.get(metric_name, {})
            }
        
        except Exception as e:
            self.logger.error(f"Error generating benchmark: {e}", exc_info=True)
            return {"error": str(e)}
    
    def answer_query(self, company_symbol: str, query: str) -> Dict:
        """Answer a general query about a company with guardrails.
        
        Args:
            company_symbol: Company symbol
            query: User query
        
        Returns:
            Dictionary with answer
        """
        try:
            # Check for greetings
            if guardrails.is_greeting(query):
                greeting_response = guardrails.handle_greeting(query)
                return {
                    "answer": greeting_response,
                    "company_symbol": company_symbol,
                    "query": query,
                    "type": "greeting"
                }
            
            # Check for advisory questions
            if guardrails.is_advisory_question(query):
                context_data = self.rag_pipeline.get_company_context(
                    company_symbol=company_symbol,
                    query=query,
                    n_results=3
                )
                refusal_response = guardrails.handle_advisory_refusal(query, context_data)
                return {
                    "answer": refusal_response,
                    "company_symbol": company_symbol,
                    "query": query,
                    "type": "advisory_refusal"
                }
            
            # Check for predictive questions
            if guardrails.is_predictive_question(query):
                refusal_response = guardrails.handle_predictive_refusal(query)
                return {
                    "answer": refusal_response,
                    "company_symbol": company_symbol,
                    "query": query,
                    "type": "predictive_refusal"
                }
            
            # Get company info
            session = db.get_session()
            try:
                company = session.query(db.Company).filter_by(
                    symbol=company_symbol.upper()
                ).first()
                if not company:
                    return {"error": f"Company {company_symbol} not found"}
                
                company_name = company.name or company_symbol
            finally:
                session.close()
            
            # Get context
            context_data = self.rag_pipeline.get_company_context(
                company_symbol=company_symbol,
                query=query,
                n_results=5
            )
            
            # Check if requested data is available
            query_lower = query.lower()
            requested_metrics = []
            for metric_name in context_data["metrics"].keys():
                if metric_name.lower() in query_lower:
                    requested_metrics.append(metric_name)
            
            # Generate prompt
            prompt = self.prompts.general_query_prompt(
                query=query,
                company_name=company_name,
                context=context_data["context_texts"],
                metrics=context_data["metrics"]
            )
            
            # Generate response
            answer = self.gemini_client.generate(
                prompt=prompt,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens
            )
            
            # Apply guardrails
            answer = guardrails.ensure_neutral_tone(answer)
            
            # Check if answer indicates data unavailable
            if "not available" in answer.lower() or "i don't know" in answer.lower() or "cannot find" in answer.lower():
                # Extract metric name if possible
                metric_name = "this information"
                for metric in requested_metrics:
                    if metric.lower() in query_lower:
                        metric_name = metric.replace("_", " ").title()
                        break
                answer = guardrails.handle_data_unavailable(metric_name)
            
            # Add citations if sources available
            sources = []
            if context_data.get("contexts"):
                for ctx in context_data["contexts"][:3]:
                    if ctx.get("metadata", {}).get("source"):
                        sources.append({
                            "type": ctx["metadata"].get("document_type", "data"),
                            "url": ctx["metadata"].get("source_url", "")
                        })
            
            if sources:
                answer = guardrails.add_citations(answer, sources)
            
            return {
                "answer": answer.strip(),
                "company_symbol": company_symbol,
                "company_name": company_name,
                "query": query,
                "type": "general"
            }
        
        except Exception as e:
            self.logger.error(f"Error answering query: {e}", exc_info=True)
            return {"error": str(e)}

