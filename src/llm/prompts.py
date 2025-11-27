"""Prompt templates for different features."""
from typing import Dict, List, Optional
from src.llm.guardrails import guardrails


class PromptTemplates:
    """Prompt templates for financial analysis features."""
    
    @staticmethod
    def quarterly_summary_prompt(company_name: str, context: List[str]) -> str:
        """Generate prompt for quarterly summary."""
        context_text = "\n\n---\n\n".join(context[:3])  # Use top 3 contexts
        
        return f"""You are a financial analyst assistant. Analyze the quarterly results for {company_name} based on the following information:

{context_text}

Provide a concise 3-4 line summary focusing on:
1. Performance vs previous quarter/year
2. Key drivers of performance
3. Overall assessment

Format: Write in clear, jargon-free language that a retail investor can understand. Be specific with numbers and percentages when available."""

    @staticmethod
    def bull_bear_case_prompt(company_name: str, sector: str, 
                             context: List[str], metrics: Dict) -> str:
        """Generate prompt for bull vs bear case."""
        context_text = "\n\n---\n\n".join(context[:5])  # Use top 5 contexts
        
        metrics_text = ""
        if metrics:
            metrics_text = "\n\nKey Financial Metrics:\n"
            for metric_name, metric_data in list(metrics.items())[:10]:
                value = metric_data.get("value")
                if value is not None:
                    metrics_text += f"- {metric_name}: {value}\n"
        
        return f"""You are a financial analyst. Analyze {company_name} in the {sector} sector.

IMPORTANT CONSTRAINTS:
- Use neutral, factual language. Avoid emotional words like "multibagger", "skyrocketing", "cheap", "jackpot", "safe"
- Do NOT provide buy/sell recommendations
- Do NOT use "you" in portfolio recommendation context
- Focus on comparative analysis, not personalized advice
- Be objective and data-driven

Context Information:
{context_text}
{metrics_text}

Provide a balanced analysis with:

BULL CASE (3-4 points):
- Strengths and competitive advantages
- Growth opportunities
- Positive indicators and trends
- Market positioning

BEAR CASE (3-4 points):
- Risks and concerns
- Competitive threats
- Negative indicators
- Potential challenges

Format: Be data-driven and specific. Use bullet points for clarity. Use neutral, professional language."""

    @staticmethod
    def red_flags_prompt(company_name: str, sector: str,
                        context: List[str], metrics: Dict,
                        benchmarks: Optional[Dict] = None) -> str:
        """Generate prompt for red flags analysis."""
        context_text = "\n\n---\n\n".join(context[:5])
        
        metrics_text = ""
        if metrics:
            metrics_text = "\n\nFinancial Metrics:\n"
            for metric_name, metric_data in list(metrics.items())[:15]:
                value = metric_data.get("value")
                if value is not None:
                    metrics_text += f"- {metric_name}: {value}\n"
        
        benchmarks_text = ""
        if benchmarks:
            benchmarks_text = "\n\nSector Benchmarks (for comparison):\n"
            for metric_name, bench_data in list(benchmarks.items())[:10]:
                median = bench_data.get("percentile_50")
                if median is not None:
                    benchmarks_text += f"- {metric_name} (Sector Median): {median}\n"
        
        return f"""You are a risk analyst. Identify potential red flags for {company_name} in the {sector} sector.

IMPORTANT CONSTRAINTS:
- Use neutral, factual language. Avoid emotional words
- Do NOT provide buy/sell recommendations
- Focus on objective risk identification
- Be specific and data-driven

Context Information:
{context_text}
{metrics_text}
{benchmarks_text}

Analyze and identify red flags if:
- Metrics deviate significantly from sector norms
- Deteriorating trends are evident
- Concerning ratios (debt, liquidity, profitability)
- Management or operational issues
- Regulatory or legal concerns

Format: List each red flag with:
1. The red flag description
2. Why it's concerning
3. Severity level (High/Medium/Low)
4. Relevant metric or data point

Be specific and data-driven. Only flag genuine concerns. Use neutral, professional language."""

    @staticmethod
    def benchmark_prompt(company_name: str, metric_name: str,
                        company_value: Optional[float],
                        sector: str, benchmarks: Dict) -> str:
        """Generate prompt for benchmark comparison."""
        bench_data = benchmarks.get(metric_name, {})
        median = bench_data.get("percentile_50")
        p25 = bench_data.get("percentile_25")
        p75 = bench_data.get("percentile_75")
        
        return f"""You are a financial analyst. Compare {metric_name} for {company_name} with the {sector} sector.

Company Value: {company_value if company_value is not None else 'Not available'}

Sector Benchmarks:
- 25th Percentile: {p25 if p25 is not None else 'Not available'}
- Median (50th Percentile): {median if median is not None else 'Not available'}
- 75th Percentile: {p75 if p75 is not None else 'Not available'}

Provide:
1. Comparison: Is the company's {metric_name} better, worse, or similar to the sector?
2. Contextual Interpretation: What does this mean for the company?
3. Implications: What are the potential implications for investors?

Format: Write in clear, actionable language. Use specific numbers and percentiles."""

    @staticmethod
    def general_query_prompt(query: str, company_name: str,
                            context: List[str], metrics: Dict) -> str:
        """Generate prompt for general queries."""
        context_text = "\n\n---\n\n".join(context[:5])
        
        metrics_text = ""
        if metrics:
            metrics_text = "\n\nRelevant Financial Metrics:\n"
            for metric_name, metric_data in list(metrics.items())[:10]:
                value = metric_data.get("value")
                if value is not None:
                    metrics_text += f"- {metric_name}: {value}\n"
        
        return f"""You are a financial analyst assistant helping an investor understand {company_name}.

CRITICAL CONSTRAINTS:
- Do NOT provide buy/sell recommendations or investment advice
- Do NOT use "you" in portfolio recommendation context (e.g., "you should buy")
- Use neutral, factual language. Avoid emotional words like "multibagger", "skyrocketing", "cheap", "jackpot"
- Do NOT predict future prices or performance
- If data is not available, clearly state that
- Focus on comparative analysis and factual information

Context Information:
{context_text}
{metrics_text}

User Question: {query}

Provide a clear, accurate, and helpful answer based on the context provided. 
- If the information is not available in the context, clearly state: "I'm still learning, this information is not available with me right now but will soon be available."
- Be specific with numbers and data when available
- Use neutral, professional language
- Do not provide investment advice or recommendations"""

