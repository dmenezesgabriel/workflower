import logging

from workflower.models.job import Job
from workflower.utils import crud

logger = logging.getLogger("workflower.job_controller")


class JobController:
    # TODO
    # ======================================================================= #
    # - add regex to logs pattern match
    # - trigger dependencies should be a trigger
    # ======================================================================= #
    @staticmethod
    def trigger_dependencies(
        session, job_id, scheduler, job_return_value, **kwargs
    ):
        """
        Trigger job's dependencies.
        """
        dependency_jobs = crud.get_all(session, Job, depends_on=job_id)
        if dependency_jobs:
            for dependency_job in dependency_jobs:
                if dependency_job.dependency_logs_pattern:
                    logger.info("Dependency job has log pattern to match")
                    # Check pattern
                    # TODO
                    # Make it as Regex
                    matches = (
                        str(dependency_job.dependency_logs_pattern).lower()
                        in job_return_value.lower()
                    )

                    # ======================================================= #
                    # | matches | run_if_pattern_match | schedule |
                    # | True    | True                 | True     |
                    # | False   | True                 | False    |
                    # | True    | False                | False    |
                    # | False   | False                | True     |
                    # ======================================================= #

                    if matches:
                        logger.info("Dependency job pattern matches")
                        if not dependency_job.run_if_pattern_match:
                            # True False
                            logger.info("Pattern matches but should not run")
                            return
                    elif not matches:
                        logger.info("Dependency job pattern did not matches")
                        if dependency_job.run_if_pattern_match:
                            # False True
                            logger.info(
                                "Pattern did not matched, should not run"
                            )
                            return

                logger.info(f"Dependency job {dependency_job.name} triggered")
                dependency_job.schedule(scheduler, **kwargs)
                Job.update_next_run_time(session, dependency_job.id, scheduler)
