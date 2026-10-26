"""
Stock Tools Module

This module contains pure functions for fetching and processing stock market data.
These functions wrap the yfinance library and provide clean, type-safe interfaces
that our Pydantic AI agents can use.

Key Concepts:
- Pure functions: Given the same input, always return the same output
- Type hints: Clear inputs and outputs
- Error handling: Gracefully handle problems (invalid symbols, network errors)
- Data transformation: Converting raw yfinance data into our Pydantic models

All functions here follow functional programming principles - they don't modify
global state and have predictable behavior.
"""

import yfinance as yf
from src.stock_analyst.models import StockData
from src.stock_analyst.constants import DEFAULT_PERIOD


def fetch_stock_data(symbol: str, period: str = DEFAULT_PERIOD) -> StockData:
    """
    Fetch stock market data for a given symbol from Yahoo Finance.
    
    This function retrieves both current and historical data, then packages it
    into a StockData model for type safety and validation.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "GOOGL")
        period: Time period for historical data (e.g., "1mo", "3mo", "1y")
                Valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    
    Returns:
        StockData object containing current and historical information
    
    Raises:
        ValueError: If the symbol is invalid or data cannot be fetched
        
    Example:
        >>> data = fetch_stock_data("AAPL", "1mo")
        >>> print(f"Current price: ${data.current_price}")
    """
    try:
        # Create a Ticker object for the symbol
        # This is yfinance's main interface for stock data
        ticker = yf.Ticker(symbol.upper())

        # Fetch historical data for the specified period
        # This returns a pandas DataFrame with columns: Open, High, Low, Close, Volume
        hist = ticker.history(period=period)

        # Validate that we got data back
        if hist.empty:
            raise ValueError(f"No data found for symbol '{symbol}'. Please check the ticker symbol.")

        # Get current stock info (this is a dictionary with lots of data)
        info = ticker.info

        # Extract the data we need and validate it exists
        # Some stocks might not have all fields, so we use .get() with defaults
        current_price = hist['Close'].iloc[-1]  # Most recent closing price
        previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)

        # Calculate price change
        price_change = current_price - previous_close
        price_change_percent = (price_change / previous_close) * 100 if previous_close != 0 else 0.0

        # Extract company name (with fallback)
        company_name = info.get('longName', info.get('shortName', symbol))

        # Convert historical prices to lists
        # We use .tolist() to convert pandas Series to Python lists
        price_history = hist['Close'].tolist()
        dates = [date.strftime('%Y-%m-%d') for date in hist.index]

        # Get volume (most recent day)
        volume = int(hist['Volume'].iloc[-1])

        # Market cap (might be None for some stocks)
        market_cap = info.get('marketCap')

        # Create and return a StockData model
        # Pydantic will validate all the types and values
        stock_data = StockData(
            symbol=symbol.upper(),
            company_name=company_name,
            current_price=round(current_price, 2),
            previous_close=round(previous_close, 2),
            price_change=round(price_change, 2),
            price_change_percent=round(price_change_percent, 2),
            volume=volume,
            market_cap=market_cap,
            price_history=price_history,
            dates=dates,
            period=period,
        )
        return stock_data
        
    except Exception as e:
        # Re-raise with a more helpful error message
        raise ValueError(f"Error fetching data for '{symbol}': {str(e)}")


def calculate_moving_average(prices: list[float], window: int) -> float | None:
    """
    Calculate the simple moving average for a list of prices.
    
    A moving average smooths out price fluctuations to show the overall trend.
    For example, a 20-day moving average is the average of the last 20 days' prices.
    
    Args:
        prices: List of prices (oldest to newest)
        window: Number of periods to average (e.g., 20 for 20-day MA)
    
    Returns:
        The moving average, or None if there aren't enough data points
        
    Example:
        >>> prices = [100, 102, 101, 103, 105]
        >>> ma = calculate_moving_average(prices, 3)
        >>> print(ma)  # Average of last 3 prices: (101 + 103 + 105) / 3 = 103.0
    """
    if len(prices) < window:
        return None
    
    # Take the last 'window' prices and calculate their average
    recent_prices = prices[-window:]
    return round(sum(recent_prices) / window, 2)


def get_price_change_percent(prices: list[float]) -> float:
    """
    Calculate the percentage change from the first to last price.
    
    This shows the overall change over the entire period.
    
    Args:
        prices: List of prices (oldest to newest)
    
    Returns:
        Percentage change (positive for gains, negative for losses)
        
    Example:
        >>> prices = [100, 110, 105, 120]
        >>> change = get_price_change_percent(prices)
        >>> print(change)  # 20.0 (from 100 to 120 is +20%)
    """
    if len(prices) < 2:
        return 0.0
    
    first_price = prices[0]
    last_price = prices[-1]
    
    if first_price == 0:
        return 0.0
    
    percent_change = ((last_price - first_price) / first_price) * 100
    return round(percent_change, 2)


def find_support_resistance(prices: list[float]) -> tuple[float | None, float | None]:
    """
    Identify basic support and resistance levels from price history.
    
    Support is where the price tends to stop falling (buyers step in).
    Resistance is where the price tends to stop rising (sellers step in).
    
    This is a simplified approach:
    - Support: Average of the lowest 20% of prices
    - Resistance: Average of the highest 20% of prices
    
    Args:
        prices: List of prices (oldest to newest)
    
    Returns:
        Tuple of (support_level, resistance_level), either can be None
        
    Example:
        >>> prices = [100, 95, 105, 98, 110, 103, 108]
        >>> support, resistance = find_support_resistance(prices)
        >>> print(f"Support: ${support}, Resistance: ${resistance}")
    """
    if len(prices) < 10:
        # Not enough data for meaningful support/resistance
        return None, None
    
    # Sort prices to find extremes
    sorted_prices = sorted(prices)
    
    # Take bottom 20% for support
    bottom_20_count = max(1, len(sorted_prices) // 5)
    support_prices = sorted_prices[:bottom_20_count]
    support = round(sum(support_prices) / len(support_prices), 2)
    
    # Take top 20% for resistance
    top_20_count = max(1, len(sorted_prices) // 5)
    resistance_prices = sorted_prices[-top_20_count:]
    resistance = round(sum(resistance_prices) / len(resistance_prices), 2)
    
    return support, resistance


def calculate_price_volatility(prices: list[float]) -> str:
    """
    Assess the volatility (how much prices fluctuate) of a stock.
    
    Volatility measures risk - high volatility means big price swings.
    
    This is a simplified approach using daily price changes:
    - Low: Average daily change < 2%
    - Medium: Average daily change 2-5%
    - High: Average daily change > 5%
    
    Args:
        prices: List of prices (oldest to newest)
    
    Returns:
        "low", "medium", or "high"
        
    Example:
        >>> prices = [100, 101, 99, 100, 102]  # Small changes
        >>> volatility = calculate_price_volatility(prices)
        >>> print(volatility)  # "low"
    """
    if len(prices) < 2:
        return "low"
    
    # Calculate daily percent changes
    daily_changes = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            change = abs((prices[i] - prices[i-1]) / prices[i-1]) * 100
            daily_changes.append(change)
    
    if not daily_changes:
        return "low"
    
    # Average daily change
    avg_change = sum(daily_changes) / len(daily_changes)
    
    # Classify volatility
    if avg_change < 2:
        return "low"
    elif avg_change < 5:
        return "medium"
    else:
        return "high"

def calculate_rsi(prices: list[float], period: int = 14) -> float | None:
    """
    Calculate the Relative Strength Index (RSI) using Wilder's smoothing.

    RSI measures momentum on a 0-100 scale by comparing the size of recent
    gains to the size of recent losses:
    - Above 70: often considered overbought
    - Below 30: often considered oversold

    Args:
        prices: List of prices (oldest to newest)
        period: Lookback window, 14 by default

    Returns:
        RSI between 0 and 100, or None if there isn't enough data
    """
    if len(prices) < period + 1:
        return None

    # Day-over-day changes, split into gains and losses
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(change, 0) for change in changes]
    losses = [max(-change, 0) for change in changes]

    # Start with a simple average of the first `period` changes
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Then smooth through the remaining days
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def fetch_stock_news(symbol: str, limit: int = 5) -> list[dict[str, str]]:
    """
    Fetch recent news articles for a stock from Yahoo Finance.

    yfinance has changed its news format between versions, so this handles
    both the older flat format and the newer nested "content" format.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        limit: Maximum number of articles to return

    Returns:
        List of dicts with 'title', 'publisher', and 'summary' keys.
        Empty list if no news is available.
    """
    try:
        raw_news = yf.Ticker(symbol.upper()).news or []
    except Exception:
        return []

    articles = []
    for item in raw_news[:limit]:
        content = item.get("content", item)
        title = content.get("title")
        if not title:
            continue

        provider = content.get("provider")
        if isinstance(provider, dict):
            publisher = provider.get("displayName")
        else:
            publisher = content.get("publisher")

        articles.append({
            "title": title,
            "publisher": publisher or "Unknown",
            "summary": content.get("summary") or "",
        })

    return articles


def calculate_ema_series(prices: list[float], window: int) -> list[float]:
    """
    Calculate an Exponential Moving Average (EMA) for every point it can.

    An EMA is like a moving average that weights recent prices more heavily.
    The result is shorter than the input: the first value lines up with
    prices[window - 1].

    Args:
        prices: List of prices (oldest to newest)
        window: EMA length (e.g., 12 or 26)

    Returns:
        List of EMA values, or an empty list if there isn't enough data
    """
    if len(prices) < window:
        return []

    multiplier = 2 / (window + 1)
    ema_values = [sum(prices[:window]) / window]  # seed with a simple average
    for price in prices[window:]:
        ema_values.append(price * multiplier + ema_values[-1] * (1 - multiplier))
    return ema_values


def calculate_macd(
    prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> dict[str, float] | None:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    - MACD line: fast EMA minus slow EMA (momentum)
    - Signal line: EMA of the MACD line
    - Histogram: MACD minus signal. Positive = bullish momentum,
      negative = bearish momentum.

    Needs at least slow + signal - 1 prices (34 with the defaults).

    Returns:
        Dict with 'macd', 'signal', 'histogram', or None if not enough data
    """
    fast_ema = calculate_ema_series(prices, fast)
    slow_ema = calculate_ema_series(prices, slow)
    if not slow_ema:
        return None

    # Line the two EMA series up so they cover the same days
    offset = slow - fast
    macd_line = [f - s for f, s in zip(fast_ema[offset:], slow_ema)]

    signal_series = calculate_ema_series(macd_line, signal)
    if not signal_series:
        return None

    macd_value = macd_line[-1]
    signal_value = signal_series[-1]
    return {
        "macd": round(macd_value, 2),
        "signal": round(signal_value, 2),
        "histogram": round(macd_value - signal_value, 2),
    }


def calculate_bollinger_bands(
    prices: list[float], window: int = 20, num_std: float = 2.0
) -> dict[str, float | str] | None:
    """
    Calculate Bollinger Bands.

    The middle band is the 20-day moving average. The upper and lower bands
    sit 2 standard deviations away. Price near the upper band can mean
    stretched high; near the lower band, stretched low. Wide bands mean
    high volatility.

    Returns:
        Dict with 'upper', 'middle', 'lower', and 'position' (where the latest
        price sits relative to the bands), or None if not enough data
    """
    import statistics

    if len(prices) < window:
        return None

    recent = prices[-window:]
    middle = sum(recent) / window
    std_dev = statistics.pstdev(recent)
    upper = middle + num_std * std_dev
    lower = middle - num_std * std_dev

    latest = prices[-1]
    if latest > upper:
        position = "above upper band"
    elif latest < lower:
        position = "below lower band"
    else:
        position = "within bands"

    return {
        "upper": round(upper, 2),
        "middle": round(middle, 2),
        "lower": round(lower, 2),
        "position": position,
    }