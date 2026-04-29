"""
Celery background tasks
"""
from app.tasks.celery_app import celery_app
from app.tasks.scrape_task import scrape_dealer_task, scrape_competitor_task

__all__ = [
    "celery_app",
    "scrape_dealer_task",
    "scrape_competitor_task",
]
