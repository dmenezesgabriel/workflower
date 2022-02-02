"""
Scheduler Factory.
"""
from workflower.scheduler.scheduler import Scheduler


def create_scheduler():
    scheduler = Scheduler()
    return scheduler
