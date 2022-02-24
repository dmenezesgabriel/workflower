import logging

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job
from workflower.operators.factory import create_operator
from workflower.plugins.factory import create_plugin

logger = logging.getLogger("workflower.application.job.commands")


class CreateJobCommand:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        name: str,
        operator: str,
        definition: dict,
        workflow=None,
        depends_on: str = None,
        dependency_logs_pattern: str = None,
        run_if_pattern_match: bool = True,
        is_active: bool = True,
        next_run_time: bool = None,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.name = name
        self.operator = operator
        self.definition = definition
        self.workflow = workflow
        self.depends_on = depends_on
        self.dependency_logs_pattern = dependency_logs_pattern
        self.run_if_pattern_match = run_if_pattern_match
        self.run_if_pattern_match = run_if_pattern_match
        self.is_active = is_active
        self.next_run_time = next_run_time

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = Job(
                    self.name,
                    self.operator,
                    self.definition,
                    self.workflow,
                    self.depends_on,
                    self.dependency_logs_pattern,
                    self.run_if_pattern_match,
                    self.is_active,
                    self.next_run_time,
                )
                uow.jobs.add(job)
                return job
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


# TODO
# Tests
class UpdateNextRunTimeCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id, scheduler):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.scheduler = scheduler

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    scheduled_job = self.scheduler.scheduler.get_job(
                        self.job_id
                    )
                    if scheduled_job:
                        job.next_run_time = scheduled_job.next_run_time

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


# TODO
# Tests
class UnscheduleJobCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id, scheduler):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.scheduler = scheduler

    def execute(self):
        logger.debug(f"Unscheduling job: {self.job_id}")
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    try:
                        self.scheduler.remove_job(self.job_id)
                    except JobLookupError:
                        logger.warning(
                            f"tried to remove {self}, "
                            "but it was not scheduled"
                        )
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


# TODO
# Tests
class ScheduleJobCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id, scheduler, kwargs):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.scheduler = scheduler
        self.kwargs

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    schedule_params = job.definition.copy()
                    schedule_kwargs = schedule_params.get("kwargs")
                    plugins = schedule_kwargs.get("plugins")
                    if plugins:
                        plugins_list = list(
                            map(
                                lambda plugin_name: create_plugin(plugin_name),
                                plugins,
                            )
                        )
                        schedule_kwargs.update(dict(plugins=plugins_list))
                    if schedule_kwargs:
                        schedule_kwargs.update(self.kwargs)

                    operator = create_operator(job.operator)
                    schedule_params.update(
                        dict(func=getattr(operator, "execute"))
                    )

                    try:
                        self.scheduler.add_job(
                            id=str(job.id), **schedule_params
                        )
                        logger.debug(f"Job {job} successfully scheduled")
                    except ConflictingIdError:
                        logger.warning(f"{job}, already scheduled, skipping.")
                    except ValueError as error:
                        # If someone set an invalid date value it will lead
                        # to this exception
                        logger.error(f"{job} value error: {error}")
                    except Exception as error:
                        logger.error(f"Error: {error}")

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
