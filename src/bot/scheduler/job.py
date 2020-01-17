from typing import Optional

from apscheduler.job import Job as BaseJob
from apscheduler.schedulers.base import BaseScheduler


class Job(BaseJob):

    def __init__(self,
                 scheduler: BaseScheduler,
                 id: Optional[str] = None,
                 group: Optional[str] = None,
                 **kwargs):
        super().__init__(scheduler, id, **kwargs)
        self.group = group or self.id
