"""
Helper utility functions
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable string"""
    if hours is None:
        return "N/A"

    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} min"
    elif hours < 24:
        return f"{hours:.1f} hrs"
    else:
        days = int(hours / 24)
        remaining_hours = hours % 24
        return f"{days}d {remaining_hours:.1f}h"


def calculate_percentage(value: float, total: float, decimal_places: int = 1) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((value / total) * 100, decimal_places)


def get_status_color(status: str) -> str:
    """Get color for status"""
    status_colors = {
        "completed": "#2ca02c",
        "in_progress": "#1f77b4",
        "pending": "#ff7f0e",
        "failed": "#d62728",
        "on_hold": "#9467bd",
        "cancelled": "#8c564b",
        "pass": "#2ca02c",
        "fail": "#d62728",
        "conditional": "#ff7f0e",
        "available": "#2ca02c",
        "in_use": "#1f77b4",
        "maintenance": "#ff7f0e",
        "offline": "#d62728"
    }
    return status_colors.get(status.lower(), "#7f7f7f")


def get_priority_color(priority: str) -> str:
    """Get color for priority"""
    priority_colors = {
        "low": "#2ca02c",
        "normal": "#1f77b4",
        "high": "#ff7f0e",
        "urgent": "#d62728",
        "critical": "#d62728"
    }
    return priority_colors.get(priority.lower(), "#7f7f7f")


def get_status_icon(status: str) -> str:
    """Get emoji icon for status"""
    status_icons = {
        "completed": "✅",
        "in_progress": "🔄",
        "pending": "⏳",
        "failed": "❌",
        "on_hold": "⏸️",
        "cancelled": "🚫",
        "pass": "✅",
        "fail": "❌",
        "conditional": "⚠️",
        "available": "✅",
        "in_use": "🔧",
        "maintenance": "⚙️",
        "offline": "🔴"
    }
    return status_icons.get(status.lower(), "⚪")


def export_to_json(data: Any, filename: str):
    """Export data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def get_date_range_filter(days: int = 30) -> tuple:
    """Get date range for filtering"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def aggregate_metrics(metrics: List[Dict[str, Any]], key: str) -> Dict[str, float]:
    """Aggregate metrics by key"""
    if not metrics:
        return {}

    result = {
        "min": min(m.get(key, 0) for m in metrics),
        "max": max(m.get(key, 0) for m in metrics),
        "avg": sum(m.get(key, 0) for m in metrics) / len(metrics),
        "total": sum(m.get(key, 0) for m in metrics)
    }
    return result


def filter_by_date_range(items: List[Any], date_field: str, start_date: datetime, end_date: datetime) -> List[Any]:
    """Filter items by date range"""
    filtered = []
    for item in items:
        item_date = getattr(item, date_field, None)
        if item_date and start_date <= item_date <= end_date:
            filtered.append(item)
    return filtered


def search_items(items: List[Any], search_term: str, search_fields: List[str]) -> List[Any]:
    """Search items by term in specified fields"""
    if not search_term:
        return items

    search_term = search_term.lower()
    results = []

    for item in items:
        for field in search_fields:
            value = str(getattr(item, field, "")).lower()
            if search_term in value:
                results.append(item)
                break

    return results


def calculate_trend(values: List[float]) -> str:
    """Calculate trend direction from values"""
    if len(values) < 2:
        return "stable"

    first_half = sum(values[:len(values)//2]) / (len(values)//2)
    second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

    diff_percent = ((second_half - first_half) / first_half) * 100

    if diff_percent > 5:
        return "increasing"
    elif diff_percent < -5:
        return "decreasing"
    else:
        return "stable"


def get_trend_icon(trend: str) -> str:
    """Get icon for trend"""
    trend_icons = {
        "increasing": "📈",
        "decreasing": "📉",
        "stable": "➡️"
    }
    return trend_icons.get(trend.lower(), "➡️")
