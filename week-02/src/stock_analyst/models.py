"""
Data Models Module

This module defines the data structures used throughout the stock analyst application.
We use Pydantic models to ensure all data is valid and type-safe.

Key Concepts:
- Pydantic models: Classes that automatically validate data
- Type hints: Declaring what type each field should be
- Literal types: Restrict a field to specific allowed values
- Optional fields: Fields that can be None (using | None)

Why use models?
- Catch errors early (before processing bad data)
- Self-documenting code (clear what data looks like)
- IDE support (autocomplete and type checking)
- Type safety: Prevent invalid data from being created
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class StockData(BaseModel):
    """
    Represents stock market data for a single symbol.
    
    This model contains both current and historical information about a stock.
    It's populated by the Data Agent using data from Yahoo Finance.
    
    Attributes:
        symbol: Stock ticker symbol (e.g., "AAPL", "GOOGL")
        company_name: Full company name (e.g., "Apple Inc.")
        current_price: Most recent closing price
        previous_close: Previous day's closing price
        price_change: Absolute price change from previous close
        price_change_percent: Percentage change from previous close
        volume: Trading volume for the most recent day
        market_cap: Total market capitalization
        price_history: List of historical closing prices
        dates: Corresponding dates for price_history
        period: Time period of historical data (e.g., "1mo", "3mo")
    """
    
    symbol: str = Field(description="Stock ticker symbol (uppercase)")
    company_name: str = Field(description="Full company name")
    current_price: float = Field(description="Most recent closing price in USD")
    previous_close: float = Field(description="Previous day's closing price in USD")
    price_change: float = Field(description="Absolute price change from previous close")
    price_change_percent: float = Field(description="Percentage change from previous close")
    volume: int = Field(description="Trading volume for the most recent day")
    market_cap: float | None = Field(default=None, description="Market capitalization in USD")
    price_history: list[float] = Field(description="Historical closing prices (oldest to newest)")
    dates: list[str] = Field(description="Dates for price history in ISO format")
    period: str = Field(description="Time period of data (e.g., '1mo', '3mo')")


class TechnicalAnalysis(BaseModel):
    """
    Represents technical analysis results for a stock.
    
    This model is the structured output from the Analysis Agent.
    It contains indicators and insights derived from the stock's price data.
    
    Attributes:
        trend: Overall trend direction (bullish, bearish, or neutral)
        trend_strength: How strong the trend is (weak, moderate, strong)
        support_level: Price level where stock tends to find buying support
        resistance_level: Price level where stock tends to face selling pressure
        moving_average_20: 20-day simple moving average
        moving_average_50: 50-day simple moving average (if enough data)
        volatility: Description of price volatility (low, medium, high)
        summary: Brief summary of the technical analysis
    """
    
    trend: Literal["bullish", "bearish", "neutral"] = Field(
        description="Overall price trend direction"
    )
    trend_strength: Literal["weak", "moderate", "strong"] = Field(
        description="Strength of the identified trend"
    )
    support_level: float | None = Field(
        default=None,
        description="Key support price level based on recent lows"
    )
    resistance_level: float | None = Field(
        default=None,
        description="Key resistance price level based on recent highs"
    )
    moving_average_20: float | None = Field(
        default=None,
        description="20-day simple moving average"
    )
    moving_average_50: float | None = Field(
        default=None,
        description="50-day simple moving average (if sufficient data)"
    )
    rsi: float | None = Field(
        default=None,
        description="14-day Relative Strength Index (0-100)"
    )
    macd: float | None = Field(
        default=None,
        description="MACD line value (12-day EMA minus 26-day EMA)"
    )
    macd_signal: float | None = Field(
        default=None,
        description="MACD signal line (9-day EMA of the MACD line)"
    )
    bollinger_upper: float | None = Field(
        default=None,
        description="Upper Bollinger Band (20-day MA plus 2 standard deviations)"
    )
    bollinger_lower: float | None = Field(
        default=None,
        description="Lower Bollinger Band (20-day MA minus 2 standard deviations)"
    )
    volatility: Literal["low", "medium", "high"] = Field(
        description="Assessment of price volatility"
    )
    summary: str = Field(
        description="Brief summary of technical findings"
    )

class NewsSummary(BaseModel):
    """
    Represents a summary of recent news about a stock.

    This is the structured output from the News Agent.

    Attributes:
        sentiment: Overall tone of the recent news
        summary: Short summary of what the news is about
        headlines: The headlines the summary is based on
    """

    sentiment: Literal["positive", "negative", "mixed", "neutral"] = Field(
        description="Overall sentiment of the recent news"
    )
    summary: str = Field(
        description="2-3 sentence summary of the main news themes"
    )
    headlines: list[str] = Field(
        default_factory=list,
        description="Recent headlines the summary is based on"
    )

class StockReport(BaseModel):
    """
    Represents a complete stock analysis report.
    
    This is the final output that combines data, analysis, and research.
    It's what gets displayed to the user in a beautiful format.
    
    Attributes:
        symbol: Stock ticker symbol
        generated_at: Timestamp when report was generated
        data: Raw stock data
        analysis: Technical analysis results
        recommendation: Investment perspective (educational, not advice!)
        explanation: Detailed explanation for students
        educational_notes: Key learning points from this analysis
    """
    
    symbol: str = Field(description="Stock ticker symbol")
    generated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO timestamp when report was generated"
    )
    data: StockData = Field(description="Stock market data")
    analysis: TechnicalAnalysis = Field(description="Technical analysis results")
    recommendation: str = Field(
        description="Educational investment perspective"
    )
    explanation: str = Field(
        description="Detailed explanation in beginner-friendly language"
    )
    educational_notes: list[str] = Field(
        default_factory=list,
        description="Key learning points for students"
    )
    news: NewsSummary | None = Field(
        default=None,
        description="Summary of recent news (None if unavailable)"
    )


class ResearchDependencies(BaseModel):
    """
    Dependencies for the Research Agent.
    
    This model bundles everything the Research Agent needs to generate insights.
    
    Attributes:
        stock_data: The raw stock data
        analysis: The technical analysis results
    """
    
    stock_data: StockData
    analysis: TechnicalAnalysis
    