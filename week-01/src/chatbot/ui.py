"""
User Interface Module

This module provides beautiful terminal UI functions using the Rich library.
All functions here are "pure" - they take input, display something, and return.

Rich is a Python library for rich text and beautiful formatting in the terminal.
It provides colors, tables, panels, progress bars, and much more!

This file is COMPLETE - you don't need to add anything here.
Study it to learn how to create professional terminal interfaces!
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import box

# Create a global console object for printing
# We'll use this throughout the UI module
console = Console()


def display_welcome() -> None:
    """
    Display a welcome banner when the chatbot starts.

    This function creates a beautiful header using Rich panels and styling.
    The panel draws a box around our welcome text with a specific style.
    """
    welcome_text = """
    # 🤖 Personal Chatbot
    
    Welcome! I'm your AI assistant powered by OpenAI.
    
    **Commands:**
    - Type your message and press Enter to chat
    - Type `quit`, `exit`, or `bye` to end the conversation
    
    Let's start chatting!
    """

    # Markdown() renders the text with markdown formatting
    # Panel() puts it in a nice box
    panel = Panel(
        Markdown(welcome_text),
        title="Welcome",
        border_style="bright_blue",
        box=box.ROUNDED,
    )

    console.print(panel)
    console.print()  # Empty line for spacing


def display_assistant_message(message: str) -> None:
    """
    Display the assistant's response in a styled panel.

    Args:
        message: The assistant's response text

    Design choice: Assistant messages get a panel (box) to make them
    stand out visually. The green color creates a pleasant contrast.
    """
    panel = Panel(
        message,
        title="🤖 Assistant",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),  # (vertical, horizontal) padding
    )

    console.print(panel)
    console.print()  # Empty line for spacing


def display_system_message(message: str, style: str = "yellow") -> None:
    """
    Display a system message (info, warnings, errors).

    Args:
        message: The system message text
        style: Color style to use (yellow for info, red for errors)

    System messages are for things like errors, loading states, or
    informational messages that aren't part of the conversation.
    """
    console.print(f"[{style}]ℹ️  {message}[/{style}]")
    console.print()


def display_error(error_message: str) -> None:
    """
    Display an error message in red.

    Args:
        error_message: Description of the error

    Errors get special treatment with red color and an error icon
    to make them immediately noticeable.
    """
    console.print(f"[bold red]❌ Error:[/bold red] {error_message}")
    console.print()


def get_user_input() -> str:
    """
    Get input from the user with a styled prompt.

    Returns:
        The user's input text (with leading/trailing whitespace removed)

    The Prompt class from Rich creates a nice looking input prompt.
    We use strip() to remove any extra whitespace from the input.
    """
    # Prompt.ask() displays a prompt and waits for user input
    user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
    return user_input.strip()


def display_loading() -> None:
    """
    Display a loading message while waiting for the API.

    This gives the user feedback that something is happening.
    The ellipsis animation is handled by Rich automatically.
    """
    console.print("[dim]🤔 Thinking...[/dim]")


def display_goodbye() -> None:
    """
    Display a farewell message when the user quits.

    A friendly goodbye creates a better user experience!
    """
    goodbye_text = """
    # 👋 Goodbye!
    
    Thanks for chatting! Come back anytime.
    """

    panel = Panel(
        Markdown(goodbye_text),
        border_style="bright_blue",
        box=box.ROUNDED,
    )

    console.print(panel)
