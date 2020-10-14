import random

from datetime import datetime, timedelta
from typing import Optional

from .job import Job

from apscheduler.schedulers.asyncio import AsyncIOScheduler as  BaseAsyncIOScheduler


class AsyncIOScheduler(BaseAsyncIOScheduler):
    def remove_jobs_by_group(self, group_id: str):
        return map(lambda x: self.remove_job(x.id), filter(lambda y: y.id.startswith(group_id), self.get_jobs()))

    def pause_jobs_by_group(self, group_id: str):
        return map(lambda x: x.pause(), filter(lambda y: y.id.startswith(group_id), self.get_jobs()))

    def get_jobs_by_group(self, group_id: str):
        return [job for job in filter(lambda x: x.id.startswith(group_id), self.get_jobs())]

    def retry_immediately(self, job_id: str):
        self.reschedule_job(job_id=job_id)

    def reschedule_group(self, group_id: str,
                         callback_time_upper_bound: Optional[int] = 30,
                         **kwargs):
        related_jobs = self.get_jobs_by_group(group_id)
        for job in related_jobs:
            callback_time = random.randint(5, callback_time_upper_bound)
            job.modify(kwargs=kwargs,
                       next_run_time=datetime.now() + timedelta(seconds=callback_time))
