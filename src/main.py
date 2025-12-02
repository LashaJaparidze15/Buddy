"""Buddy - Your Smart Daily Planner CLI."""

import typer
from typing import Optional
from datetime import date

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.models import init_db
from src.core import (
    ActivityManager,
    ReportGenerator,
    CompletionManager,
    AnalyticsEngine,
    SmartSuggestions,
)
from src.config import CATEGORIES, RECURRENCE_OPTIONS, get_settings
from src.config.settings import save_user_preferences, load_user_preferences
from src.utils import (
    parse_date,
    format_date,
    create_activity_table,
    print_success,
    print_error,
    print_warning,
    print_info,
)

# App info
__version__ = "1.0.0"
__app_name__ = "Buddy"

# Initialize Typer app
app = typer.Typer(
    name="buddy",
    help="🗓️  Buddy - Your Smart Daily Planner\n\nManage activities, get daily reports, track progress, and receive smart suggestions.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


# ============================================================================
# ACTIVITY COMMANDS
# ============================================================================

@app.command()
def add(
    title: str = typer.Argument(..., help="Activity title"),
    time: str = typer.Option(..., "--time", "-t", help="Start time (e.g., 09:00 or 9am)"),
    category: str = typer.Option("Other", "--category", "-c", help="Category"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Duration in minutes"),
    recurrence: str = typer.Option("once", "--recurrence", "-r", help="once/daily/weekdays/weekends/weekly"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Location"),
    prep: int = typer.Option(15, "--prep", "-p", help="Reminder minutes before"),
    outdoor: bool = typer.Option(False, "--outdoor", "-o", help="Is this an outdoor activity?"),
    description: Optional[str] = typer.Option(None, "--desc", help="Description"),
):
    """Add a new activity to your schedule."""
    try:
        manager = ActivityManager()
        activity = manager.create(
            title=title,
            start_time=time,
            category=category,
            duration=duration,
            recurrence=recurrence,
            location=location,
            prep_time=prep,
            is_outdoor=outdoor,
            description=description,
        )
        manager.close()
        
        print_success(f"Added: {activity.title} at {activity.start_time.strftime('%H:%M')}")
        
        if recurrence != "once":
            print_info(f"Repeats: {recurrence}")
            
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command(name="list")
def list_activities(
    week: bool = typer.Option(False, "--week", "-w", help="Show this week's activities"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    all_activities: bool = typer.Option(False, "--all", "-a", help="Show all activities"),
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Show activities for specific date"),
):
    """List your scheduled activities."""
    manager = ActivityManager()
    
    try:
        if all_activities:
            activities = manager.get_all(active_only=False)
            title = "All Activities"
        elif category:
            activities = manager.get_by_category(category)
            title = f"Activities: {category}"
        elif week:
            activities = manager.get_for_week()
            title = "This Week's Activities"
        elif date_str:
            target = parse_date(date_str)
            activities = manager.get_for_date(target)
            title = f"Activities for {format_date(target)}"
        else:
            activities = manager.get_for_today()
            title = f"Today's Activities ({format_date(date.today())})"
        
        if not activities:
            print_warning("No activities found.")
        else:
            table = create_activity_table(activities, title)
            console.print(table)
            console.print(f"\n[dim]Total: {len(activities)} activities[/dim]")
        
    except ValueError as e:
        print_error(str(e))
    finally:
        manager.close()


@app.command()
def show(
    activity_id: int = typer.Argument(..., help="Activity ID"),
):
    """Show detailed information about an activity."""
    manager = ActivityManager()
    activity = manager.get_by_id(activity_id)
    manager.close()
    
    if not activity:
        print_error(f"Activity #{activity_id} not found.")
        raise typer.Exit(1)
    
    console.print(f"\n[bold cyan]Activity #{activity.id}[/bold cyan]")
    console.print(f"[bold]{activity.title}[/bold]\n")
    
    details = Table(show_header=False, box=box.SIMPLE)
    details.add_column("Field", style="dim")
    details.add_column("Value")
    
    details.add_row("Time", activity.start_time.strftime("%H:%M"))
    details.add_row("Category", activity.category)
    details.add_row("Duration", activity.duration_formatted)
    details.add_row("Recurrence", activity.recurrence)
    details.add_row("Location", activity.location or "-")
    details.add_row("Prep Time", f"{activity.prep_time} min")
    details.add_row("Outdoor", "Yes" if activity.is_outdoor else "No")
    details.add_row("Active", "Yes" if activity.is_active else "No")
    details.add_row("Description", activity.description or "-")
    
    console.print(details)


@app.command()
def edit(
    activity_id: int = typer.Argument(..., help="Activity ID to edit"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    time: Optional[str] = typer.Option(None, "--time", "-t", help="New time"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="New category"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="New duration"),
    recurrence: Optional[str] = typer.Option(None, "--recurrence", "-r", help="New recurrence"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="New location"),
    prep: Optional[int] = typer.Option(None, "--prep", "-p", help="New prep time"),
    outdoor: Optional[bool] = typer.Option(None, "--outdoor", "-o", help="Outdoor activity"),
):
    """Edit an existing activity."""
    manager = ActivityManager()
    
    try:
        activity = manager.update(
            activity_id=activity_id,
            title=title,
            start_time=time,
            category=category,
            duration=duration,
            recurrence=recurrence,
            location=location,
            prep_time=prep,
            is_outdoor=outdoor,
        )
        
        if activity:
            print_success(f"Updated: {activity.title}")
        else:
            print_error(f"Activity #{activity_id} not found.")
            raise typer.Exit(1)
            
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        manager.close()


@app.command()
def delete(
    activity_id: int = typer.Argument(..., help="Activity ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete an activity."""
    manager = ActivityManager()
    activity = manager.get_by_id(activity_id)
    
    if not activity:
        print_error(f"Activity #{activity_id} not found.")
        manager.close()
        raise typer.Exit(1)
    
    if not force:
        confirm = typer.confirm(f"Delete '{activity.title}'?")
        if not confirm:
            print_info("Cancelled.")
            manager.close()
            return
    
    manager.delete(activity_id)
    manager.close()
    print_success(f"Deleted: {activity.title}")


@app.command()
def toggle(
    activity_id: int = typer.Argument(..., help="Activity ID to toggle"),
):
    """Enable or disable an activity."""
    manager = ActivityManager()
    activity = manager.toggle(activity_id)
    manager.close()
    
    if activity:
        status = "enabled" if activity.is_active else "disabled"
        print_success(f"{activity.title} is now {status}")
    else:
        print_error(f"Activity #{activity_id} not found.")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search activities by title or description."""
    manager = ActivityManager()
    activities = manager.search(query)
    manager.close()
    
    if not activities:
        print_warning(f"No activities matching '{query}'")
    else:
        table = create_activity_table(activities, f"Search: '{query}'")
        console.print(table)


# ============================================================================
# TRACKING COMMANDS
# ============================================================================

@app.command()
def mark(
    activity_id: int = typer.Argument(..., help="Activity ID"),
    status: str = typer.Argument(..., help="Status: done, missed, partial, rescheduled"),
    note: Optional[str] = typer.Option(None, "--note", "-n", help="Add a note"),
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Date (default: today)"),
):
    """Mark an activity as done, missed, partial, or rescheduled."""
    try:
        target_date = parse_date(date_str) if date_str else None
        
        manager = CompletionManager()
        activity_manager = ActivityManager()
        
        activity = activity_manager.get_by_id(activity_id)
        if not activity:
            print_error(f"Activity #{activity_id} not found.")
            raise typer.Exit(1)
        
        completion = manager.mark(
            activity_id=activity_id,
            status=status,
            target_date=target_date,
            notes=note,
        )
        
        manager.close()
        activity_manager.close()
        
        if completion:
            status_icons = {
                "done": "✅",
                "missed": "❌",
                "partial": "⚠️",
                "rescheduled": "📅",
            }
            icon = status_icons.get(completion.status, "•")
            print_success(f"{icon} Marked '{activity.title}' as {completion.status}")
            if note:
                print_info(f"Note: {note}")
        else:
            print_error("Failed to mark activity.")
            
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def review(
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Date to review (default: today)"),
):
    """Interactive end-of-day review for activities."""
    target_date = parse_date(date_str) if date_str else date.today()
    
    activity_manager = ActivityManager()
    completion_manager = CompletionManager()
    
    activities = activity_manager.get_for_date(target_date)
    
    if not activities:
        print_warning(f"No activities scheduled for {format_date(target_date)}")
        activity_manager.close()
        completion_manager.close()
        return
    
    console.print(f"\n[bold]📋 Review for {format_date(target_date)}[/bold]\n")
    
    for activity in activities:
        current_status = completion_manager.get_completion_status(activity.id, target_date)
        status_display = f"[dim]({current_status})[/dim]" if current_status else "[dim](not marked)[/dim]"
        
        console.print(f"[cyan]{activity.start_time.strftime('%H:%M')}[/cyan] - [bold]{activity.title}[/bold] {status_display}")
        
        status = typer.prompt(
            "  Status (done/missed/partial/rescheduled/skip)",
            default="skip"
        )
        
        if status.lower() == "skip":
            continue
        
        note = typer.prompt("  Note (optional)", default="")
        
        try:
            completion_manager.mark(
                activity_id=activity.id,
                status=status,
                target_date=target_date,
                notes=note if note else None,
            )
            print_success(f"  Marked as {status}")
        except ValueError as e:
            print_error(f"  {str(e)}")
        
        console.print()
    
    stats = completion_manager.get_stats(target_date, target_date)
    console.print(f"\n[bold]Summary:[/bold] {stats['done']} done, {stats['missed']} missed, {stats['partial']} partial")
    
    activity_manager.close()
    completion_manager.close()


@app.command()
def history(
    activity_id: int = typer.Argument(..., help="Activity ID"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of records to show"),
):
    """Show completion history for an activity."""
    activity_manager = ActivityManager()
    completion_manager = CompletionManager()
    
    activity = activity_manager.get_by_id(activity_id)
    if not activity:
        print_error(f"Activity #{activity_id} not found.")
        raise typer.Exit(1)
    
    completions = completion_manager.get_for_activity(activity_id, limit=limit)
    streak = completion_manager.get_streak(activity_id)
    
    console.print(f"\n[bold]📊 History: {activity.title}[/bold]")
    console.print(f"[dim]Current streak: {streak} days[/dim]\n")
    
    if completions:
        table = Table(box=box.SIMPLE)
        table.add_column("Date", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Notes", style="dim")
        
        status_icons = {
            "done": "[green]✅ done[/green]",
            "missed": "[red]❌ missed[/red]",
            "partial": "[yellow]⚠️ partial[/yellow]",
            "rescheduled": "[blue]📅 rescheduled[/blue]",
        }
        
        for c in completions:
            table.add_row(
                c.date.strftime("%Y-%m-%d"),
                status_icons.get(c.status, c.status),
                c.notes or "-",
            )
        
        console.print(table)
    else:
        print_warning("No completion history yet.")
    
    activity_manager.close()
    completion_manager.close()


# ============================================================================
# REPORT & ANALYTICS COMMANDS
# ============================================================================

@app.command()
def report(
    no_weather: bool = typer.Option(False, "--no-weather", help="Hide weather section"),
    no_news: bool = typer.Option(False, "--no-news", help="Hide news section"),
    no_stocks: bool = typer.Option(False, "--no-stocks", help="Hide stocks section"),
    no_holidays: bool = typer.Option(False, "--no-holidays", help="Hide holidays section"),
    no_activities: bool = typer.Option(False, "--no-activities", help="Hide activities section"),
    no_quote: bool = typer.Option(False, "--no-quote", help="Hide motivational quote"),
    news_count: int = typer.Option(5, "--news-count", "-n", help="Number of news headlines"),
):
    """Generate your personalized daily morning report."""
    generator = ReportGenerator()
    
    generator.generate(
        show_weather=not no_weather,
        show_news=not no_news,
        show_stocks=not no_stocks,
        show_holidays=not no_holidays,
        show_activities=not no_activities,
        show_quote=not no_quote,
        news_count=news_count,
    )
    
    generator.close()


@app.command()
def analytics(
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Date within the week to analyze"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Compare with previous week"),
):
    """Show weekly analytics, insights, and progress charts."""
    target_date = parse_date(date_str) if date_str else None
    
    engine = AnalyticsEngine()
    
    if compare:
        comparison = engine.compare_weeks(target_date)
        engine.display_report(target_date)
        
        change = comparison["rate_change"]
        if change > 0:
            print_success(f"📈 Up {change}% from last week!")
        elif change < 0:
            print_warning(f"📉 Down {abs(change)}% from last week")
        else:
            print_info("↔️ Same as last week")
    else:
        engine.display_report(target_date)
    
    engine.close()


@app.command()
def suggest(
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Date for suggestions"),
):
    """Get smart, context-aware suggestions for your day."""
    target_date = parse_date(date_str) if date_str else None
    
    suggestions = SmartSuggestions()
    suggestions.display_suggestions(target_date)
    suggestions.close()


# ============================================================================
# CONFIG & UTILITY COMMANDS
# ============================================================================

@app.command()
def categories():
    """List all available activity categories."""
    console.print("\n[bold]Available Categories:[/bold]\n")
    for cat in CATEGORIES:
        console.print(f"  • {cat}")
    console.print()


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Set your location"),
    units: Optional[str] = typer.Option(None, "--units", "-u", help="Weather units: metric or imperial"),
    report_time: Optional[str] = typer.Option(None, "--report-time", help="Morning report time (HH:MM)"),
    review_time: Optional[str] = typer.Option(None, "--review-time", help="Evening review time (HH:MM)"),
):
    """View or update your Buddy configuration."""
    settings = get_settings()
    
    if show or (not location and not units and not report_time and not review_time):
        # Show current config
        console.print("\n[bold]⚙️ Current Configuration[/bold]\n")
        
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Location", settings.location)
        table.add_row("Weather Units", settings.weather_units)
        table.add_row("Report Time", settings.report_time)
        table.add_row("Review Time", settings.review_time)
        table.add_row("Prep Time", f"{settings.prep_time} minutes")
        table.add_row("Week Start", settings.week_start.capitalize())
        table.add_row("", "")
        table.add_row("Weather API", "✓ Set" if settings.weather_api_key else "✗ Not set")
        table.add_row("News API", "✓ Set" if settings.news_api_key else "✗ Not set")
        table.add_row("Stocks API", "✓ Set" if settings.stocks_api_key else "✗ Not set")
        
        console.print(table)
        console.print("\n[dim]Use --location, --units, etc. to update settings[/dim]\n")
        return
    
    # Update settings
    updates = {}
    
    if location:
        updates["location"] = location
        print_success(f"Location set to: {location}")
    
    if units:
        if units.lower() in ["metric", "imperial"]:
            updates["weather_units"] = units.lower()
            print_success(f"Weather units set to: {units}")
        else:
            print_error("Units must be 'metric' or 'imperial'")
    
    if report_time:
        updates["report_time"] = report_time
        print_success(f"Report time set to: {report_time}")
    
    if review_time:
        updates["review_time"] = review_time
        print_success(f"Review time set to: {review_time}")
    
    if updates:
        save_user_preferences(updates)


@app.command(name="init")
def initialize():
    """Initialize the Buddy database."""
    init_db()
    print_info("Run 'buddy add' to create your first activity!")


@app.command()
def version():
    """Show Buddy version information."""
    console.print(f"\n[bold cyan]{__app_name__}[/bold cyan] v{__version__}")
    console.print("[dim]Your Smart Daily Planner[/dim]\n")


@app.command()
def status():
    """Show a quick status overview."""
    activity_manager = ActivityManager()
    completion_manager = CompletionManager()
    
    today = date.today()
    activities_today = activity_manager.get_for_today()
    
    # Get today's completions
    completed = 0
    for activity in activities_today:
        status = completion_manager.get_completion_status(activity.id, today)
        if status == "done":
            completed += 1
    
    console.print(f"\n[bold]📊 Quick Status - {format_date(today)}[/bold]\n")
    console.print(f"  Activities today: {len(activities_today)}")
    console.print(f"  Completed: {completed}/{len(activities_today)}")
    
    # Next upcoming activity
    from datetime import datetime
    now = datetime.now().time()
    upcoming = [a for a in activities_today if a.start_time > now]
    
    if upcoming:
        next_activity = upcoming[0]
        console.print(f"  Next up: {next_activity.title} at {next_activity.start_time.strftime('%H:%M')}")
    
    # Quick suggestions count
    suggestions = SmartSuggestions()
    all_suggestions = suggestions.get_all_suggestions()
    high_priority = [s for s in all_suggestions if s.priority == "high"]
    suggestions.close()
    
    if high_priority:
        console.print(f"\n  [yellow]⚠️ {len(high_priority)} important suggestion(s) - run 'buddy suggest'[/yellow]")
    
    console.print()
    
    activity_manager.close()
    completion_manager.close()


# Entry point
def main():
    app()


if __name__ == "__main__":
    main()