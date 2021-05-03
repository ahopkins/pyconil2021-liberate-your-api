from __future__ import annotations

from uuid import uuid4

import ujson as json

from .log import logger
from .task import Task


class Job:
    def __init__(self, task: str, backend, uid=None, kwargs=None) -> None:
        self.task = task
        self.uid = uid or uuid4()
        self.backend = backend
        self.kwargs = kwargs

    async def execute(self, task: Task):
        logger.info(f"Executing {self.task}")
        await task.run(**self.kwargs)

    async def __aenter__(self):
        task_class = Task.__registry__.get(self.task)
        if task_class:
            task = task_class()
            await self.backend.start(self)
            return task
        else:
            raise Exception(f"No task named {self.task}")

    async def __aexit__(self, *_):
        await self.backend.stop(self)

    @classmethod
    async def create(cls, job: str, backend):
        data = json.loads(job)
        task = data.pop("task")
        instance = cls(task, backend, **data)
        async with instance as task:
            await instance.execute(task)
