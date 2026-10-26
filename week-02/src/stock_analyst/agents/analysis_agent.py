"""
Analysis Agent Module

This module defines the Analysis Agent, which performs technical analysis on stock data.
It uses Pydantic AI with structured outputs to ensure the analysis follows a consistent format.

Key Concepts:
- Structured Outputs: The agent returns a specific Pydantic model (TechnicalAnalysis)
- result_type: Tells the agent what structure its response should have
- Technical Analysis: Using price patterns and indicators to assess trends
- Tools: Helper functions for calculating indicators

The Analysis Agent takes stock data and produces a TechnicalAnalysis report
with trend direction, support/resistance levels, and other insights.
"""

from pydantic_ai import Agent, RunContext
from src.stock_analyst.models import StockData, TechnicalAnalysis
from src.stock_analyst.tools.stock_tools import (
    calculate_moving_average,
    find_support_resistance,
    calculate_price_volatility,
    get_price_change_percent,
)
from src.stock_analyst.constants import ANALYSIS_AGENT_PROMPT
from src.stock_analyst.llm import llm
from src.utils.debug import debug_log

from src.stock_analyst.tools.stock_tools import (
    calculate_moving_average,
    find_support_resistance,
    calculate_price_volatility,
    get_price_change_percent,
    calculate_rsi,
    calculate_ema_series,
    calculate_macd,
    calculate_bollinger_bands,
)
# Create the Analysis Agent with structured output
# - result_type: This tells the agent to return a TechnicalAnalysis object
# - The agent will use its tools to calculate indicators
# - It will then structure its findings into the TechnicalAnalysis model
analysis_agent = Agent(
    model=llm,
    deps_type=StockData,  # Takes StockData as dependency
    output_type=TechnicalAnalysis,   # Returns structured TechnicalAnalysis
    retries=2,
    system_prompt=ANALYSIS_AGENT_PROMPT,
)


@analysis_agent.tool
def calculate_ma_20(ctx: RunContext[StockData]) -> float | None:
    """
    Calculate the 20-day moving average.

    A moving average smooths out price fluctuations to show the trend.
    The 20-day MA is commonly used for short-term trends.

    Args:
        ctx: Run context containing StockData

    Returns:
        20-day moving average, or None if insufficient data
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "calculate_ma_20"]')
    result = calculate_moving_average(stock_data.price_history, 20)
    return result


@analysis_agent.tool
def calculate_ma_50(ctx: RunContext[StockData]) -> float | None:
    """
    Calculate the 50-day moving average.

    The 50-day MA is used for medium-term trends.
    When price crosses above/below the MA, it can signal trend changes.

    Args:
        ctx: Run context containing StockData

    Returns:
        50-day moving average, or None if insufficient data
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "calculate_ma_50"]')
    result = calculate_moving_average(stock_data.price_history, 50)
    return result


@analysis_agent.tool
def get_support_and_resistance(ctx: RunContext[StockData]) -> dict[str, float | None]:
    """
    Calculate support and resistance levels.

    Support: Price level where buying pressure tends to prevent further decline
    Resistance: Price level where selling pressure tends to prevent further increase

    Args:
        ctx: Run context containing StockData

    Returns:
        Dictionary with 'support' and 'resistance' keys
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "get_support_and_resistance"]')
    support, resistance = find_support_resistance(stock_data.price_history)

    return {
        "support": support,
        "resistance": resistance,
    }


@analysis_agent.tool
def assess_volatility(ctx: RunContext[StockData]) -> str:
    """
    Assess the price volatility.

    Volatility measures how much the price fluctuates.
    High volatility = more risk but potentially more reward.

    Args:
        ctx: Run context containing StockData

    Returns:
        "low", "medium", or "high"
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "assess_volatility"]')
    result = calculate_price_volatility(stock_data.price_history)
    return result


@analysis_agent.tool
def get_overall_price_change(ctx: RunContext[StockData]) -> float:
    """
    Calculate the overall price change percentage.
    
    This shows the total change from the beginning to end of the period.
    
    Args:
        ctx: Run context containing StockData
    
    Returns:
        Percentage change (positive for gains, negative for losses)
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "get_overall_price_change"]')
    return get_price_change_percent(stock_data.price_history)

@analysis_agent.tool
def calculate_rsi_14(ctx: RunContext[StockData]) -> float | None:
    """
    Calculate the 14-day Relative Strength Index (RSI).

    RSI is a momentum indicator on a 0-100 scale. Above 70 is often
    considered overbought (price may be stretched upward); below 30 is
    often considered oversold.

    Args:
        ctx: Run context containing StockData

    Returns:
        RSI value between 0 and 100, or None if insufficient data
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "calculate_rsi_14"]')
    return calculate_rsi(stock_data.price_history, 14)

@analysis_agent.tool
def get_macd(ctx: RunContext[StockData]) -> dict[str, float] | None:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    MACD shows momentum. When the MACD line is above its signal line
    (positive histogram), momentum is bullish; below it (negative
    histogram), momentum is bearish.

    Args:
        ctx: Run context containing StockData

    Returns:
        Dict with 'macd', 'signal', and 'histogram', or None if insufficient data
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "get_macd"]')
    return calculate_macd(stock_data.price_history)


@analysis_agent.tool
def get_bollinger_bands(ctx: RunContext[StockData]) -> dict[str, float | str] | None:
    """
    Calculate Bollinger Bands (20-day, 2 standard deviations).

    Price above the upper band can signal an overstretched rally; below
    the lower band can signal an overstretched drop. Wide bands mean
    high volatility.

    Args:
        ctx: Run context containing StockData

    Returns:
        Dict with 'upper', 'middle', 'lower', and 'position', or None
        if insufficient data
    """
    stock_data = ctx.deps
    debug_log('[agent: "analysis_agent"] [tool-call: "get_bollinger_bands"]')
    return calculate_bollinger_bands(stock_data.price_history)

@analysis_agent.tool
def get_current_vs_ma_position(ctx: RunContext[StockData]) -> dict[str, str]:
    """
    Determine if current price is above or below moving averages.
    
    This helps identify trends:
    - Price above MA = potential uptrend
    - Price below MA = potential downtrend
    
    Args:
        ctx: Run context containing StockData
    
    Returns:
        Dictionary describing position relative to MAs
    """
    stock_data = ctx.deps
    current_price = stock_data.current_price

    debug_log('[agent: "analysis_agent"] [tool-call: "get_current_vs_ma_position"]')
    ma_20 = calculate_moving_average(stock_data.price_history, 20)
    ma_50 = calculate_moving_average(stock_data.price_history, 50)
    
    result = {}
    
    if ma_20:
        if current_price > ma_20:
            result["vs_ma_20"] = "above"
        elif current_price < ma_20:
            result["vs_ma_20"] = "below"
        else:
            result["vs_ma_20"] = "at"
    
    if ma_50:
        if current_price > ma_50:
            result["vs_ma_50"] = "above"
        elif current_price < ma_50:
            result["vs_ma_50"] = "below"
        else:
            result["vs_ma_50"] = "at"
    
    return result


async def analyze_stock(stock_data: StockData) -> TechnicalAnalysis:
    """
    Analyze stock data and produce a technical analysis report.

    This is the main interface for getting technical analysis.
    It runs the Analysis Agent with the stock data and returns structured results.

    Args:
        stock_data: The stock data to analyze

    Returns:
        TechnicalAnalysis object with trend, indicators, and insights

    Example usage:
        >>> stock_data = await fetch_stock_data_with_agent("AAPL")
        >>> analysis = await analyze_stock(stock_data)
        >>> print(f"Trend: {analysis.trend}")
        >>> print(f"Support: ${analysis.support_level}")
    """
    print("Running Analysis Agent...")

    # Run the agent with a clear instruction
    # The agent will use its tools to calculate indicators
    # Then it will structure the findings into a TechnicalAnalysis object
    result = await analysis_agent.run(
        f"Perform technical analysis on {stock_data.symbol}. "
        f"Use the available tools to calculate moving averages, RSI, MACD, Bollinger Bands, support/resistance, "
        f"volatility, and price trends. Then provide a structured analysis with "
        f"trend direction, trend strength, key levels, and a summary.",
        deps=stock_data,
    )

    # result.output contains the structured TechnicalAnalysis object
    analysis = result.output

    print("✅ Analysis Agent completed successfully")
    return analysis



