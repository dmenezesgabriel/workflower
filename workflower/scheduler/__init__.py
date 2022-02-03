"""
Scheduler Factory.
"""
from workflower.scheduler.scheduler import SchedulerService


def create_scheduler():
    scheduler = SchedulerService()
    return scheduler
