"""Output formatting utilities."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def create_activity_table(activities: list, title: str = "Activities") -> Table:
    """Create a formatted table for displaying activities."""
    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    
    table.add_column("ID", style="dim", width=4)
    table.add_column("Time", style="cyan", width=6)
    table.add_column("Title", style="bold white", min_width=20)
    table.add_column("Category", style="magenta", width=10)
    table.add_column("Duration", style="green", width=8)
    table.add_column("Recurs", style="yellow", width=10)
    
    for activity in activities:
        table.add_row(
            str(activity.id),
            activity.start_time.strftime("%H:%M"),
            activity.title,
            activity.category,
            activity.duration_formatted,
            activity.recurrence,
        )
    
    return table


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_header(title: str) -> None:
    """Print a section header."""
    console.print(Panel(title, style="bold blue", box=box.DOUBLE))