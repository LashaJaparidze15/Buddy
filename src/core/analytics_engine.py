"""Analytics engine for weekly reports and insights."""

from datetime import date, timedelta
from typing import Optional
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.models import Activity, Completion, SessionLocal
from src.utils import get_week_bounds, format_date


class AnalyticsEngine:
    """Generate analytics and insights from activity data."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.console = Console()
    
    def get_weekly_data(
        self,
        target_date: Optional[date] = None
    ) -> dict:
        """Get all data for a week."""
        week_start, week_end = get_week_bounds(target_date)
        
        # Get all completions for the week
        completions = (
            self.db.query(Completion)
            .filter(Completion.date >= week_start)
            .filter(Completion.date <= week_end)
            .all()
        )
        
        # Get all activities
        activities = self.db.query(Activity).filter(Activity.is_active == True).all()
        
        return {
            "week_start": week_start,
            "week_end": week_end,
            "completions": completions,
            "activities": activities,
        }
    
    def calculate_stats(self, target_date: Optional[date] = None) -> dict:
        """Calculate comprehensive statistics for a week."""
        data = self.get_weekly_data(target_date)
        completions = data["completions"]
        
        total = len(completions)
        
        if total == 0:
            return {
                "week_start": data["week_start"],
                "week_end": data["week_end"],
                "total": 0,
                "done": 0,
                "missed": 0,
                "partial": 0,
                "rescheduled": 0,
                "completion_rate": 0.0,
                "by_category": {},
                "by_day": {},
                "best_day": None,
                "worst_day": None,
            }
        
        # Count by status
        done = sum(1 for c in completions if c.status == "done")
        missed = sum(1 for c in completions if c.status == "missed")
        partial = sum(1 for c in completions if c.status == "partial")
        rescheduled = sum(1 for c in completions if c.status == "rescheduled")
        
        # Completion rate (done + half of partial)
        completion_rate = ((done + partial * 0.5) / total) * 100
        
        # Stats by category
        by_category = self._calculate_category_stats(completions)
        
        # Stats by day of week
        by_day = self._calculate_day_stats(completions)
        
        # Best and worst days
        best_day = None
        worst_day = None
        if by_day:
            sorted_days = sorted(by_day.items(), key=lambda x: x[1]["rate"], reverse=True)
            best_day = sorted_days[0][0] if sorted_days[0][1]["rate"] > 0 else None
            worst_day = sorted_days[-1][0] if sorted_days[-1][1]["total"] > 0 else None
        
        return {
            "week_start": data["week_start"],
            "week_end": data["week_end"],
            "total": total,
            "done": done,
            "missed": missed,
            "partial": partial,
            "rescheduled": rescheduled,
            "completion_rate": round(completion_rate, 1),
            "by_category": by_category,
            "by_day": by_day,
            "best_day": best_day,
            "worst_day": worst_day,
        }
    
    def _calculate_category_stats(self, completions: list[Completion]) -> dict:
        """Calculate stats grouped by category."""
        category_data = defaultdict(lambda: {"done": 0, "total": 0})
        
        for completion in completions:
            activity = self.db.query(Activity).filter(Activity.id == completion.activity_id).first()
            if activity:
                category = activity.category
                category_data[category]["total"] += 1
                if completion.status == "done":
                    category_data[category]["done"] += 1
                elif completion.status == "partial":
                    category_data[category]["done"] += 0.5
        
        # Calculate rates
        result = {}
        for category, data in category_data.items():
            rate = (data["done"] / data["total"] * 100) if data["total"] > 0 else 0
            result[category] = {
                "done": int(data["done"]),
                "total": data["total"],
                "rate": round(rate, 1),
            }
        
        return result
    
    def _calculate_day_stats(self, completions: list[Completion]) -> dict:
        """Calculate stats grouped by day of week."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_data = {day: {"done": 0, "total": 0} for day in days}
        
        for completion in completions:
            day_name = completion.date.strftime("%A")
            day_data[day_name]["total"] += 1
            if completion.status == "done":
                day_data[day_name]["done"] += 1
            elif completion.status == "partial":
                day_data[day_name]["done"] += 0.5
        
        # Calculate rates
        result = {}
        for day, data in day_data.items():
            if data["total"] > 0:
                rate = (data["done"] / data["total"] * 100)
                result[day] = {
                    "done": int(data["done"]),
                    "total": data["total"],
                    "rate": round(rate, 1),
                }
        
        return result
    
    def get_streaks(self) -> list[dict]:
        """Get streak information for all activities."""
        activities = self.db.query(Activity).filter(Activity.is_active == True).all()
        streaks = []
        
        for activity in activities:
            streak = self._calculate_streak(activity.id)
            streaks.append({
                "activity_id": activity.id,
                "title": activity.title,
                "category": activity.category,
                "streak": streak,
            })
        
        return sorted(streaks, key=lambda x: x["streak"], reverse=True)
    
    def _calculate_streak(self, activity_id: int) -> int:
        """Calculate current streak for an activity."""
        completions = (
            self.db.query(Completion)
            .filter(Completion.activity_id == activity_id)
            .filter(Completion.status == "done")
            .order_by(Completion.date.desc())
            .all()
        )
        
        if not completions:
            return 0
        
        streak = 0
        expected_date = date.today()
        
        for completion in completions:
            if completion.date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif completion.date < expected_date:
                break
        
        return streak
    
    def get_insights(self, stats: dict) -> list[str]:
        """Generate insights from statistics."""
        insights = []
        
        # Overall performance
        rate = stats["completion_rate"]
        if rate >= 80:
            insights.append("🌟 Excellent week! You completed over 80% of your activities.")
        elif rate >= 60:
            insights.append("👍 Good progress this week! Keep pushing to reach 80%.")
        elif rate >= 40:
            insights.append("💪 Room for improvement. Try breaking activities into smaller tasks.")
        elif stats["total"] > 0:
            insights.append("🎯 Challenging week. Consider reducing the number of activities.")
        
        # Best category
        if stats["by_category"]:
            best_cat = max(stats["by_category"].items(), key=lambda x: x[1]["rate"])
            if best_cat[1]["rate"] > 0:
                insights.append(f"🏆 Best category: {best_cat[0]} ({best_cat[1]['rate']}% completion)")
        
        # Worst category
        if stats["by_category"] and len(stats["by_category"]) > 1:
            worst_cat = min(stats["by_category"].items(), key=lambda x: x[1]["rate"])
            if worst_cat[1]["rate"] < 50:
                insights.append(f"📉 Needs attention: {worst_cat[0]} ({worst_cat[1]['rate']}% completion)")
        
        # Best day
        if stats["best_day"]:
            insights.append(f"📅 Most productive day: {stats['best_day']}")
        
        # Missed activities
        if stats["missed"] > stats["done"]:
            insights.append("⚠️ More activities missed than completed. Review your schedule.")
        
        return insights
    
    def display_report(self, target_date: Optional[date] = None) -> None:
        """Display a formatted analytics report."""
        stats = self.calculate_stats(target_date)
        
        # Header
        self.console.print()
        self.console.print(Panel(
            f"[bold]Week of {format_date(stats['week_start'])} - {format_date(stats['week_end'])}[/bold]",
            title="📊 [bold cyan]Weekly Analytics[/bold cyan] 📊",
            box=box.DOUBLE,
        ))
        
        if stats["total"] == 0:
            self.console.print("\n[yellow]No activity data for this week.[/yellow]")
            self.console.print("[dim]Mark some activities as done/missed to see analytics![/dim]\n")
            return
        
        # Overview
        self.console.print("\n[bold]📈 OVERVIEW[/bold]")
        self.console.print("─" * 40)
        
        # Progress bar
        rate = stats["completion_rate"]
        filled = int(rate / 5)
        bar = "█" * filled + "░" * (20 - filled)
        color = "green" if rate >= 70 else "yellow" if rate >= 50 else "red"
        self.console.print(f"Completion Rate: [{color}]{bar}[/{color}] {rate}%")
        
        self.console.print(f"\nTotal Activities: {stats['total']}")
        self.console.print(f"  [green]✅ Done:[/green] {stats['done']}")
        self.console.print(f"  [red]❌ Missed:[/red] {stats['missed']}")
        self.console.print(f"  [yellow]⚠️ Partial:[/yellow] {stats['partial']}")
        self.console.print(f"  [blue]📅 Rescheduled:[/blue] {stats['rescheduled']}")
        
        # By Category
        if stats["by_category"]:
            self.console.print("\n[bold]📁 BY CATEGORY[/bold]")
            self.console.print("─" * 40)
            
            table = Table(box=box.SIMPLE, show_header=True)
            table.add_column("Category", style="white")
            table.add_column("Done", justify="right", style="green")
            table.add_column("Total", justify="right")
            table.add_column("Rate", justify="right")
            
            for category, data in sorted(stats["by_category"].items(), key=lambda x: x[1]["rate"], reverse=True):
                rate_color = "green" if data["rate"] >= 70 else "yellow" if data["rate"] >= 50 else "red"
                table.add_row(
                    category,
                    str(data["done"]),
                    str(data["total"]),
                    f"[{rate_color}]{data['rate']}%[/{rate_color}]",
                )
            
            self.console.print(table)
        
        # By Day
        if stats["by_day"]:
            self.console.print("\n[bold]📅 BY DAY[/bold]")
            self.console.print("─" * 40)
            
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days_order:
                if day in stats["by_day"]:
                    data = stats["by_day"][day]
                    bar_len = int(data["rate"] / 10)
                    bar = "▓" * bar_len + "░" * (10 - bar_len)
                    color = "green" if data["rate"] >= 70 else "yellow" if data["rate"] >= 50 else "red"
                    self.console.print(f"{day[:3]}: [{color}]{bar}[/{color}] {data['rate']}%")
        
        # Streaks
        streaks = self.get_streaks()
        active_streaks = [s for s in streaks if s["streak"] > 0]
        
        if active_streaks:
            self.console.print("\n[bold]🔥 ACTIVE STREAKS[/bold]")
            self.console.print("─" * 40)
            
            for s in active_streaks[:5]:
                self.console.print(f"  {s['streak']} days - {s['title']}")
        
        # Insights
        insights = self.get_insights(stats)
        if insights:
            self.console.print("\n[bold]💡 INSIGHTS[/bold]")
            self.console.print("─" * 40)
            
            for insight in insights:
                self.console.print(f"  {insight}")
        
        self.console.print()
    
    def compare_weeks(self, current_date: Optional[date] = None) -> dict:
        """Compare current week with previous week."""
        if current_date is None:
            current_date = date.today()
        
        current_stats = self.calculate_stats(current_date)
        previous_date = current_date - timedelta(days=7)
        previous_stats = self.calculate_stats(previous_date)
        
        rate_change = current_stats["completion_rate"] - previous_stats["completion_rate"]
        
        return {
            "current": current_stats,
            "previous": previous_stats,
            "rate_change": round(rate_change, 1),
            "improved": rate_change > 0,
        }
    
    def close(self):
        """Close database session."""
        self.db.close()