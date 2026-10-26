"""
User Interface Module

This module provides beautiful terminal UI functions using the Rich library.
All functions here display information in a visually appealing, easy-to-read format.

Rich is a Python library for rich text and beautiful formatting in the terminal.
It provides colors, tables, panels, progress bars, and much more!

This module creates a professional-looking stock analysis interface that makes
learning about stocks engaging and accessible.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import box
from src.stock_analyst.models import StockData, StockReport
from src.stock_analyst.constants import EXAMPLE_STOCKS


# Create a global console object for printing
console = Console()


def display_welcome() -> None:
    """
    Display a welcome banner when the stock analyst starts.
    
    This creates an engaging header that introduces the tool and its capabilities.
    """
    welcome_text = """
    # 📈 Stock Market Analyst
    
    Welcome! I'm an AI-powered stock market analyst built with **Pydantic AI**.
    
    I can help you analyze stocks by:
    - 📊 Fetching real-time market data
    - 🔍 Performing technical analysis
    - 💡 Generating educational insights
    
    **Popular Stocks to Try:**
    """ + ", ".join([f"`{symbol}`" for symbol in EXAMPLE_STOCKS[:6]]) + """
    
    **Commands:**
    - Enter a stock symbol to analyze (e.g., AAPL, GOOGL, TSLA)
    - Type `quit`, `exit`, or `bye` to end the session
    
    *Disclaimer: This tool is for educational purposes only, not financial advice.*
    """
    
    panel = Panel(
        Markdown(welcome_text),
        title="Welcome to Stock Analyst",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    
    console.print(panel)
    console.print()


def display_loading(message: str = "Analyzing...") -> None:
    """
    Display a loading message while processing.
    
    Args:
        message: Custom loading message
    """
    console.print(f"[dim]⏳ {message}[/dim]")


def display_error(error_message: str) -> None:
    """
    Display an error message in red.
    
    Args:
        error_message: Description of the error
    """
    console.print(f"[bold red]❌ Error:[/bold red] {error_message}")
    console.print()


def get_stock_symbol() -> str:
    """
    Prompt the user for a stock symbol.
    
    Returns:
        The user's input (uppercase, stripped)
    """
    symbol = Prompt.ask("[bold cyan]Enter stock symbol[/bold cyan]")
    return symbol.strip().upper()


def display_stock_header(data: StockData) -> None:
    """
    Display the stock's basic information in a header panel.
    
    Args:
        data: StockData object with current information
    """
    # Determine color based on price change
    if data.price_change >= 0:
        change_color = "green"
        arrow = "↑"
    else:
        change_color = "red"
        arrow = "↓"
    
    # Format market cap
    if data.market_cap:
        if data.market_cap >= 1_000_000_000_000:  # Trillions
            market_cap_str = f"${data.market_cap / 1_000_000_000_000:.2f}T"
        elif data.market_cap >= 1_000_000_000:  # Billions
            market_cap_str = f"${data.market_cap / 1_000_000_000:.2f}B"
        else:  # Millions
            market_cap_str = f"${data.market_cap / 1_000_000:.2f}M"
    else:
        market_cap_str = "N/A"
    
    # Create header text
    header = f"""
[bold white]{data.company_name}[/bold white] ([cyan]{data.symbol}[/cyan])

[bold white]${data.current_price}[/bold white]  [{change_color}]{arrow} ${abs(data.price_change)} ({data.price_change_percent:+.2f}%)[/{change_color}]

Market Cap: {market_cap_str} | Volume: {data.volume:,} | Period: {data.period}
"""
    
    panel = Panel(
        header.strip(),
        border_style="bright_blue",
        box=box.ROUNDED,
    )
    
    console.print(panel)


def display_price_chart(data: StockData) -> None:
    """
    Display a simple price table showing recent history.
    
    Args:
        data: StockData with price history
    """
    # Create a table for recent prices
    table = Table(title="Recent Price History", box=box.SIMPLE)
    
    table.add_column("Date", style="cyan")
    table.add_column("Close Price", justify="right", style="white")
    table.add_column("Change", justify="right")
    
    # Show last 10 data points
    recent_count = min(10, len(data.price_history))
    for i in range(-recent_count, 0):
        date = data.dates[i]
        price = data.price_history[i]
        
        # Calculate change from previous day
        if i > -recent_count:
            prev_price = data.price_history[i - 1]
            change = price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
            
            if change >= 0:
                change_str = f"[green]+${change:.2f} (+{change_pct:.2f}%)[/green]"
            else:
                change_str = f"[red]${change:.2f} ({change_pct:.2f}%)[/red]"
        else:
            change_str = "[dim]-[/dim]"
        
        table.add_row(date, f"${price:.2f}", change_str)
    
    console.print(table)
    console.print()


def display_technical_analysis(report: StockReport) -> None:
    """
    Display the technical analysis results.
    
    Args:
        report: StockReport with analysis data
    """
    analysis = report.analysis
    
    # Choose color based on trend
    trend_colors = {
        "bullish": "green",
        "bearish": "red",
        "neutral": "yellow",
    }
    trend_color = trend_colors.get(analysis.trend, "white")
    
    # Choose emoji based on trend
    trend_emojis = {
        "bullish": "📈",
        "bearish": "📉",
        "neutral": "➡️",
    }
    trend_emoji = trend_emojis.get(analysis.trend, "📊")
    
    # Build analysis text
    analysis_text = f"""
{trend_emoji} [bold {trend_color}]{analysis.trend.upper()}[/bold {trend_color}] ({analysis.trend_strength} strength)

[bold]Volatility:[/bold] {analysis.volatility.capitalize()}

[bold]Technical Indicators:[/bold]
"""
    
    if analysis.moving_average_20:
        analysis_text += f"\n• 20-Day MA: ${analysis.moving_average_20:.2f}"
    
    if analysis.moving_average_50:
        analysis_text += f"\n• 50-Day MA: ${analysis.moving_average_50:.2f}"
    
    if analysis.rsi is not None:
        analysis_text += f"\n• RSI (14): {analysis.rsi:.1f}"

    if analysis.macd is not None and analysis.macd_signal is not None:
        analysis_text += f"\n• MACD: {analysis.macd:.2f} (signal: {analysis.macd_signal:.2f})"

    if analysis.bollinger_upper is not None and analysis.bollinger_lower is not None:
        analysis_text += (
            f"\n• Bollinger Bands: ${analysis.bollinger_lower:.2f} - ${analysis.bollinger_upper:.2f}"
        )
    
    if analysis.support_level:
        analysis_text += f"\n• Support Level: ${analysis.support_level:.2f}"
    
    if analysis.resistance_level:
        analysis_text += f"\n• Resistance Level: ${analysis.resistance_level:.2f}"
    
    analysis_text += f"\n\n[bold]Summary:[/bold]\n{analysis.summary}"
    
    panel = Panel(
        analysis_text.strip(),
        title="📊 Technical Analysis",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    
    console.print(panel)


def display_research_insights(report: StockReport) -> None:
    """
    Display the research insights and recommendations.
    
    Args:
        report: StockReport with research data
    """
    insights_text = f"""
[bold]Educational Perspective:[/bold]
{report.recommendation}

[bold]Detailed Explanation:[/bold]
{report.explanation}
"""
    
    panel = Panel(
        insights_text.strip(),
        title="💡 Research Insights",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    
    console.print(panel)


def display_educational_notes(report: StockReport) -> None:
    """
    Display educational learning points.
    
    Args:
        report: StockReport with educational notes
    """
    if not report.educational_notes:
        return
    
    notes_text = "\n\n".join([f"• {note}" for note in report.educational_notes])
    
    panel = Panel(
        notes_text,
        title="📚 Learning Points",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    
    console.print(panel)

def display_news(report: StockReport) -> None:
    """
    Display the news summary, if available.

    Args:
        report: StockReport with optional news data
    """
    if not report.news:
        return

    sentiment_colors = {
        "positive": "green",
        "negative": "red",
        "mixed": "yellow",
        "neutral": "white",
    }
    color = sentiment_colors.get(report.news.sentiment, "white")

    news_text = f"[bold]Sentiment:[/bold] [{color}]{report.news.sentiment.upper()}[/{color}]"
    news_text += f"\n\n{report.news.summary}"

    if report.news.headlines:
        news_text += "\n\n[bold]Recent Headlines:[/bold]"
        for headline in report.news.headlines:
            news_text += f"\n• {headline}"

    panel = Panel(
        news_text,
        title="📰 Recent News",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    console.print(panel)

def display_stock_report(report: StockReport) -> None:
    """
    Display a complete stock analysis report.
    
    This is the main display function that shows all components of the analysis
    in a beautiful, organized format.
    
    Args:
        report: Complete StockReport object
    """
    console.print()
    console.print("[bold bright_blue]" + "=" * 70 + "[/bold bright_blue]")
    console.print()
    
    # Display each section
    display_stock_header(report.data)
    console.print()
    
    display_price_chart(report.data)
    
    display_technical_analysis(report)
    console.print()
    
    display_research_insights(report)
    console.print()

    display_news(report)
    console.print()
    
    display_educational_notes(report)
    console.print()
    
    console.print("[bold bright_blue]" + "=" * 70 + "[/bold bright_blue]")
    console.print()


def display_goodbye() -> None:
    """
    Display a farewell message when the user quits.
    """
    goodbye_text = """
    # 👋 Goodbye!
    
    Thanks for using Stock Market Analyst!
    
    Remember: Always do your own research before making investment decisions.
    Happy learning! 📚
    """
    
    panel = Panel(
        Markdown(goodbye_text),
        border_style="bright_blue",
        box=box.ROUNDED,
    )
    
    console.print(panel)


def ask_continue() -> bool:
    """
    Ask if the user wants to analyze another stock.
    
    Returns:
        True if the user wants to continue, False otherwise
    """
    response = Prompt.ask(
        "\n[bold cyan]Analyze another stock?[/bold cyan]",
        choices=["y", "n"],
        default="y"
    )
    return response.lower() == "y"

