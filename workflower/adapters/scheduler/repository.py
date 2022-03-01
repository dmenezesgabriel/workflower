class APSchedulerRepository:
    def __init__(self, scheduler) -> None:
        self.scheduler = scheduler

    def add_job(self, func, *args, **kwargs):
        return self.scheduler.add_job(func, *args, **kwargs)

    def modify_job(self, job_id, jobstore=None, **changes):
        return self.scheduler.modify_job(job_id, jobstore, **changes)

    def reschedule_job(
        self, job_id, jobstore=None, trigger=None, **trigger_args
    ):
        return self.scheduler.reschedule_job(
            job_id, jobstore, trigger, **trigger_args
        )

    def pause_job(self, job_id, jobstore=None):
        return self.scheduler.pause_job(job_id, jobstore)

    def resume_job(self, job_id, jobstore=None):
        return self.scheduler.resume_job(job_id, jobstore)

    def remove_job(self, job_id, jobstore=None):
        self.scheduler.remove_job(job_id, jobstore)

    def get_job(self, job_id):
        return self.scheduler.get_job(job_id)

    def get_jobs(self, jobstore=None):
        return self.scheduler.get_jobs(jobstore)
