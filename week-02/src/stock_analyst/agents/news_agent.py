"""
News Agent Module

This module defines the News Agent, which fetches and summarizes recent news
about a stock. It follows the same pattern as the other agents:
a tool that fetches data, plus structured output.
"""

from pydantic_ai import Agent, RunContext
from src.stock_analyst.models import StockData, NewsSummary
from src.stock_analyst.tools.stock_tools import fetch_stock_news
from src.stock_analyst.constants import NEWS_AGENT_PROMPT
from src.stock_analyst.llm import llm
from src.utils.debug import debug_log


news_agent = Agent(
    model=llm,
    deps_type=StockData,
    output_type=NewsSummary,
    retries=2,
    system_prompt=NEWS_AGENT_PROMPT,
)


@news_agent.tool
def get_recent_news(ctx: RunContext[StockData]) -> list[dict[str, str]]:
    """
    Fetch recent news articles for the stock being analyzed.

    Args:
        ctx: Run context containing StockData

    Returns:
        List of articles, each with 'title', 'publisher', and 'summary'
    """
    stock_data = ctx.deps
    debug_log('[agent: "news_agent"] [tool-call: "get_recent_news"]')
    return fetch_stock_news(stock_data.symbol)


async def fetch_news_with_agent(stock_data: StockData) -> NewsSummary:
    """
    Run the News Agent to summarize recent news for a stock.

    Args:
        stock_data: The stock data (used to know which symbol to look up)

    Returns:
        NewsSummary with sentiment, summary, and headlines
    """
    print("Running News Agent...")

    result = await news_agent.run(
        f"Fetch and summarize recent news about {stock_data.company_name} "
        f"({stock_data.symbol}). Judge the overall sentiment and list the headlines.",
        deps=stock_data,
    )

    print("✅ News Agent completed successfully")
    return result.output