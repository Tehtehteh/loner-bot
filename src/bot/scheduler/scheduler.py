from .job import Job

from apscheduler.schedulers.asyncio import AsyncIOScheduler as  BaseAsyncIOScheduler


class AsyncIOScheduler(BaseAsyncIOScheduler):
    def remove_jobs_by_group(self, group_id: str):
        for job in filter(lambda x: isinstance(x, Job), self.get_jobs()):  # type: Job
            if job.group == group_id:
                self.remove_job(job.id)

    def pause_jobs_by_group(self, group_id: str):
        for job in filter(lambda x: isinstance(x, Job), self.get_jobs()):  # type: Job
            if job.group == group_id:
                job.pause()

    def get_jobs_by_group(self, group_id: str):
        return [job for job in filter(lambda x: isinstance(x, Job) and job.group == group_id, self.get_jobs())]
