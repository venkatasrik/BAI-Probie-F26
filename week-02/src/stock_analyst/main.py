"""
Main Module

This is the entry point of the stock analyst application. It orchestrates the
three AI agents (Data, Analysis, Research) to provide comprehensive stock analysis.

Key Concepts:
- Agent Orchestration: Coordinating multiple agents to work together
- Async/Await: Using asynchronous programming for API calls
- Error Handling: Gracefully managing errors at each step
- User Experience: Creating a smooth, interactive CLI flow

The main loop:
1. Get stock symbol from user
2. Run Data Agent to fetch stock data
3. Run Analysis Agent to perform technical analysis
4. Run Research Agent to generate insights
5. Display beautiful report
6. Ask if user wants to analyze another stock
"""

import asyncio
from src.stock_analyst.models import StockReport
from src.stock_analyst.agents.data_agent import fetch_stock_data_with_agent
from src.stock_analyst.agents.analysis_agent import analyze_stock
from src.stock_analyst.agents.research_agent import generate_research_report
from src.stock_analyst import ui
from src.utils.debug import debug_log

from src.stock_analyst.agents.news_agent import fetch_news_with_agent

def should_quit(user_input: str) -> bool:
    """
    Check if the user wants to quit the application.
    
    Args:
        user_input: The user's input
        
    Returns:
        True if user wants to quit, False otherwise
    """
    quit_commands = {"quit", "exit", "bye", "q"}
    return user_input.lower() in quit_commands


async def generate_stock_report(symbol: str) -> StockReport:
    """
    Orchestrate all three agents to analyze a stock symbol.

    This function coordinates the Data, Analysis, and Research agents to produce
    a complete stock analysis report.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        period: Time period for historical data (e.g., "1mo", "3mo")

    Returns:
        Complete StockReport with data, analysis, and insights

    Raises:
        ValueError: If the symbol is invalid or analysis fails

    Process:
        1. Data Agent fetches stock data from Yahoo Finance
        2. Analysis Agent performs technical analysis on the data
        3. Research Agent generates insights and recommendations
        4. All results are combined into a StockReport
    """
    # Step 1: Fetch stock data
    ui.display_loading("Step 1 of 3: Fetching stock data...")
    stock_data = await fetch_stock_data_with_agent(symbol)

    # Step 2: Perform technical analysis
    ui.display_loading("Step 2 of 3: Analyzing stock data and market trends...")
    analysis = await analyze_stock(stock_data)

        # Step 3: Generate research insights
    ui.display_loading("Step 3 of 4: Generating report...")
    research = await generate_research_report(stock_data, analysis)

    # Step 4: Summarize recent news (optional - don't fail the report if this breaks)
    ui.display_loading("Step 4 of 4: Checking recent news...")
    try:
        news = await fetch_news_with_agent(stock_data)
    except Exception as e:
        debug_log(f"News Agent failed: {e}")
        news = None

    report = StockReport(
        symbol=stock_data.symbol,
        data=stock_data,
        analysis=analysis,
        recommendation=research["recommendation"],
        explanation=research["explanation"],
        news=news,
    )
    return report


async def run_analysis_loop() -> None:
    """
    Main analysis loop - the heart of the application!

    This function:
    1. Displays the welcome message
    2. Gets stock symbol from user
    3. Orchestrates the agents to analyze the stock
    4. Displays the beautiful report
    5. Asks if user wants to continue
    6. Handles errors gracefully
    """
    ui.display_welcome()

    while True:
        try:
            # Get stock symbol from user
            symbol = ui.get_stock_symbol()

            # Check if user wants to quit
            if should_quit(symbol):
                debug_log("User requested to quit")
                ui.display_goodbye()
                break

            # Validate input
            if not symbol:
                ui.display_error("Please enter a stock symbol!")
                continue

            # Analyze the stock
            try:
                report = await generate_stock_report(symbol)
                # Display the complete report
                ui.display_stock_report(report)

            except ValueError as e:
                ui.display_error(str(e))
                continue
            except Exception as e:
                ui.display_error(f"An unexpected error occurred: {str(e)}")
                continue

            # Ask if user wants to continue
            if not ui.ask_continue():
                ui.display_goodbye()
                break
            else:
                debug_log("User chose to continue - starting new analysis loop")
                
        except KeyboardInterrupt:
            # User pressed Ctrl+C
            print()  # New line after ^C
            ui.display_goodbye()
            break
        except Exception as e:
            # Unexpected error in the main loop
            ui.display_error(f"Fatal error: {str(e)}")
            break


def main() -> None:
    """
    Entry point for the stock analyst application.

    This function is called when you run: python -m src.stock_analyst.main
    It sets up the async environment and runs the main loop.
    """
    try:
        # Run the conversational loop
        asyncio.run(run_analysis_loop())
    except KeyboardInterrupt:
        print("\n")
        ui.display_goodbye()
    except Exception as e:
        ui.display_error(f"Failed to start: {str(e)}")

if __name__ == "__main__":
    main()

