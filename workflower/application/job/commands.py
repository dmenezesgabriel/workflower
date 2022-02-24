import logging
import traceback

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
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


class ChangeJobStatusCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id, status):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.status = status

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    job.status = self.status
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


class DeactivateJobCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id):
        self.unit_of_work = unit_of_work
        self.job_id = job_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    job.is_active = False
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


class RemoveJobCommand:
    def __init__(self, unit_of_work: UnitOfWork, job_id):
        self.unit_of_work = unit_of_work
        self.job_id = job_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    uow.jobs.remove(job)
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


class UpdateJobStatusCommand:
    # Added
    # Scheduled
    # Running
    # Executed
    # Removed
    pass


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
                    scheduled_job = self.scheduler.get_job(self.job_id)
                    if scheduled_job:
                        job.next_run_time = scheduled_job.next_run_time

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


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
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


# TODO
# Tests
class ScheduleJobCommand:
    def __init__(
        self, unit_of_work: UnitOfWork, job_id, scheduler, kwargs=None
    ):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.scheduler = scheduler
        self.kwargs = kwargs

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    schedule_params = job.definition.copy()
                    schedule_kwargs = schedule_params.get("kwargs")
                    schedule_kwargs.update(dict(job_id=job.id))
                    plugins = schedule_kwargs.get("plugins")
                    if plugins:
                        plugins_list = list(
                            map(
                                lambda plugin_name: create_plugin(plugin_name),
                                plugins,
                            )
                        )
                        schedule_kwargs.update(dict(plugins=plugins_list))
                    if schedule_kwargs and self.kwargs:
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
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")


# TODO
# Tests
class GetDependencyTriggerJobsCommand:
    def __init__(
        self, unit_of_work: UnitOfWork, job_id, job_return_value, kwargs=None
    ):
        self.unit_of_work = unit_of_work
        self.job_id = job_id
        self.job_id = job_id
        self.job_return_value = job_return_value
        self.kwargs = kwargs

    def execute(self):
        try:
            dependency_jobs_to_trigger = []
            with self.unit_of_work as uow:
                job = uow.jobs.get(id=self.job_id)
                if job:
                    dependency_jobs = uow.jobs.list(depends_on=self.job_id)
                    if dependency_jobs:
                        for dependency_job in dependency_jobs:
                            if dependency_job.dependency_logs_pattern:
                                logger.info(
                                    "Dependency job has log pattern to match"
                                )
                                # Check pattern
                                # TODO
                                # Make it as Regex
                                matches = (
                                    str(
                                        dependency_job.dependency_logs_pattern
                                    ).lower()
                                    in self.job_return_value.lower()
                                )

                                # ================================== ======== #
                                # | matches | run_if_pattern_match | schedule |
                                # | True    | True                 | True     |
                                # | False   | True                 | False    |
                                # | True    | False                | False    |
                                # | False   | False                | True     |
                                # =========================================== #

                                if matches:
                                    logger.debug(
                                        "Dependency job pattern matches"
                                    )
                                    if not dependency_job.run_if_pattern_match:
                                        # True False
                                        logger.debug(
                                            "Pattern matches but should"
                                            " not run"
                                        )
                                        continue
                                elif not matches:
                                    logger.debug(
                                        "Dependency job pattern did "
                                        "not matches"
                                    )
                                    if dependency_job.run_if_pattern_match:
                                        # False True
                                        logger.debug(
                                            "Pattern did not matched, should"
                                            " not run"
                                        )
                                        continue

                            logger.info(
                                f"Dependency job {dependency_job.name} "
                                "triggered"
                            )
                            dependency_jobs_to_trigger.append(dependency_job)
            return dependency_jobs_to_trigger
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception:
            logger.error(f"Error: {traceback.print_exc()}")
