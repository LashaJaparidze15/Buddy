"""Daily report generator combining all services."""

import random
from datetime import date, datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.core.activity_manager import ActivityManager
from src.services import WeatherService, NewsService, StocksService, HolidaysService


class ReportGenerator:
    """Generate daily morning reports."""
    
    MOTIVATIONAL_QUOTES = [
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("It's not about perfect. It's about effort.", "Jillian Michaels"),
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Your limitation—it's only your imagination.", "Unknown"),
        ("Push yourself, because no one else is going to do it for you.", "Unknown"),
        ("Great things never come from comfort zones.", "Unknown"),
        ("Dream it. Wish it. Do it.", "Unknown"),
        ("Success doesn't just find you. You have to go out and get it.", "Unknown"),
        ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown"),
        ("Don't stop when you're tired. Stop when you're done.", "Unknown"),
        ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
        ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
        ("Little things make big days.", "Unknown"),
        ("It's going to be hard, but hard does not mean impossible.", "Unknown"),
    ]
    
    def __init__(self):
        self.console = Console()
        self.weather_service = WeatherService()
        self.news_service = NewsService()
        self.stocks_service = StocksService()
        self.holidays_service = HolidaysService()
        self.activity_manager = ActivityManager()
    
    def _get_greeting(self) -> str:
        """Get time-appropriate greeting."""
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"
    
    def _get_quote(self) -> tuple[str, str]:
        """Get random motivational quote."""
        return random.choice(self.MOTIVATIONAL_QUOTES)
    
    def _format_date_header(self) -> str:
        """Format current date as header."""
        today = date.today()
        return today.strftime("%A, %B %d, %Y")
    
    def generate(
        self,
        show_weather: bool = True,
        show_news: bool = True,
        show_stocks: bool = True,
        show_holidays: bool = True,
        show_activities: bool = True,
        show_quote: bool = True,
        news_count: int = 5,
    ) -> None:
        """Generate and display the daily report."""
        
        # Header
        greeting = self._get_greeting()
        date_str = self._format_date_header()
        
        self.console.print()
        self.console.print(Panel(
            f"[bold white]{greeting}![/bold white]\n[dim]{date_str}[/dim]",
            title="🌟 [bold cyan]Buddy Daily Report[/bold cyan] 🌟",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        
        # Weather Section
        if show_weather:
            self._print_weather_section()
        
        # Today's Activities
        if show_activities:
            self._print_activities_section()
        
        # Upcoming Holidays
        if show_holidays:
            self._print_holidays_section()
        
        # News Section
        if show_news:
            self._print_news_section(count=news_count)
        
        # Stocks Section
        if show_stocks:
            self._print_stocks_section()
        
        # Motivational Quote
        if show_quote:
            self._print_quote_section()
        
        self.console.print()
    
    def _print_weather_section(self) -> None:
        """Print weather section."""
        self.console.print("\n[bold yellow]☀️  WEATHER[/bold yellow]")
        self.console.print("─" * 40)
        
        weather = self.weather_service.get_current()
        
        if weather:
            self.console.print(weather.detailed())
            
            # Weather suggestion
            suggestion = self.weather_service.get_weather_suggestion()
            if suggestion:
                self.console.print(f"\n[italic]{suggestion}[/italic]")
        else:
            self.console.print("[dim]Weather data unavailable. Check API key.[/dim]")
    
    def _print_activities_section(self) -> None:
        """Print today's activities."""
        self.console.print("\n[bold green]📋  TODAY'S ACTIVITIES[/bold green]")
        self.console.print("─" * 40)
        
        activities = self.activity_manager.get_for_today()
        
        if activities:
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
            table.add_column("Time", style="cyan", width=6)
            table.add_column("Activity", style="white")
            table.add_column("Category", style="magenta", width=10)
            
            for activity in activities:
                table.add_row(
                    activity.start_time.strftime("%H:%M"),
                    activity.title,
                    activity.category,
                )
            
            self.console.print(table)
            self.console.print(f"[dim]Total: {len(activities)} activities[/dim]")
        else:
            self.console.print("[dim]No activities scheduled for today.[/dim]")
            self.console.print("[dim]Use 'buddy add' to schedule something![/dim]")
    
    def _print_holidays_section(self) -> None:
        """Print upcoming holidays."""
        holidays = self.holidays_service.get_upcoming(days_ahead=7)
        
        if holidays:
            self.console.print("\n[bold magenta]🎉  UPCOMING HOLIDAYS[/bold magenta]")
            self.console.print("─" * 40)
            
            for holiday in holidays:
                self.console.print(holiday.summary())
    
    def _print_news_section(self, count: int = 5) -> None:
        """Print news headlines."""
        self.console.print("\n[bold blue]📰  TOP NEWS[/bold blue]")
        self.console.print("─" * 40)
        
        articles = self.news_service.get_top_headlines(count=count)
        
        if articles:
            for i, article in enumerate(articles, 1):
                self.console.print(f"{i}. {article.title}")
                self.console.print(f"   [dim]{article.source}[/dim]")
        else:
            self.console.print("[dim]News unavailable. Check API key.[/dim]")
    
    def _print_stocks_section(self) -> None:
        """Print stock market summary."""
        self.console.print("\n[bold cyan]📈  MARKET WATCH[/bold cyan]")
        self.console.print("─" * 40)
        
        # Try to get market indices
        summary = self.stocks_service.get_market_summary()
        
        has_data = False
        for name, quote in summary.items():
            if quote:
                has_data = True
                self.console.print(f"{name}: {quote.summary()}")
        
        if not has_data:
            self.console.print("[dim]Stock data unavailable. Check API key.[/dim]")
    
    def _print_quote_section(self) -> None:
        """Print motivational quote."""
        quote, author = self._get_quote()
        
        self.console.print()
        self.console.print(Panel(
            f"[italic]\"{quote}\"[/italic]\n[dim]— {author}[/dim]",
            title="💡 [bold]Quote of the Day[/bold]",
            box=box.ROUNDED,
            padding=(1, 2),
        ))
    
    def generate_text(self) -> str:
        """Generate report as plain text (for email/export)."""
        lines = []
        today = date.today()
        
        lines.append("=" * 50)
        lines.append(f"BUDDY DAILY REPORT - {today.strftime('%A, %B %d, %Y')}")
        lines.append("=" * 50)
        
        # Weather
        weather = self.weather_service.get_current()
        lines.append("\n☀️  WEATHER")
        lines.append("-" * 30)
        if weather:
            lines.append(f"Location: {weather.location}")
            lines.append(f"Temperature: {weather.temperature}{weather.temp_unit}")
            lines.append(f"Conditions: {weather.description}")
        else:
            lines.append("Weather data unavailable")
        
        # Activities
        activities = self.activity_manager.get_for_today()
        lines.append("\n📋  TODAY'S ACTIVITIES")
        lines.append("-" * 30)
        if activities:
            for a in activities:
                lines.append(f"{a.start_time.strftime('%H:%M')} - {a.title} ({a.category})")
        else:
            lines.append("No activities scheduled")
        
        # Holidays
        holidays = self.holidays_service.get_upcoming(days_ahead=7)
        if holidays:
            lines.append("\n🎉  UPCOMING HOLIDAYS")
            lines.append("-" * 30)
            for h in holidays:
                lines.append(f"{h.date.strftime('%b %d')} - {h.name}")
        
        # Quote
        quote, author = self._get_quote()
        lines.append("\n💡  QUOTE OF THE DAY")
        lines.append("-" * 30)
        lines.append(f"\"{quote}\"")
        lines.append(f"— {author}")
        
        lines.append("\n" + "=" * 50)
        
        return "\n".join(lines)
    
    def close(self):
        """Clean up resources."""
        self.activity_manager.close()