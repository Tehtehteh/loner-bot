from .job import Job

from apscheduler.schedulers.asyncio import AsyncIOScheduler as  BaseAsyncIOScheduler


class AsyncIOScheduler(BaseAsyncIOScheduler):
    def remove_jobs_by_group(self, group_id: str):
        return map(lambda x: self.remove_job(x.id), filter(lambda y: y.id.startswith(group_id), self.get_jobs()))

    def pause_jobs_by_group(self, group_id: str):
        return map(lambda x: x.pause(), filter(lambda y: y.id.startswith(group_id), self.get_jobs()))

    def get_jobs_by_group(self, group_id: str):
        return [job for job in filter(lambda x: x.id.startswith(group_id), self.get_jobs())]
