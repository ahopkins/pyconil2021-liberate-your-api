from __future__ import annotations

import asyncio
import os
from asyncio import Task as AsyncTask
from multiprocessing import Process, Queue
from queue import Empty
from typing import List

import ujson as json

from .backend import FileBackend
from .job import Job
from .log import logger

STOP = "__STOP__"
TIMEOUT = 3


class Scheduler:
    def __init__(self, queue, loop, backend) -> None:
        self.queue = queue
        self.tasks: List[AsyncTask] = []
        self._loop = loop
        self.backend = backend

    async def run(self):
        logger.info("> Starting job manager")
        while True:
            await self._loop.run_in_executor(None, self.consumer)
            await asyncio.sleep(0)

    def consumer(
        self,
    ):
        try:
            job = self.queue.get(timeout=1)
        except Empty:
            return

        if job == STOP:
            logger.info("> Stopping consumer")
            self.queue.put_nowait(job)
        else:
            logger.info(f"> Job requested: {job=}")
            self.execute(job)

    def execute(self, job: str):
        task = self._loop.create_task(Job.create(job, self.backend))
        self.tasks.append(task)


def manage(queue):
    logger.info(f"Starting SAJE worker [{os.getpid()}]")
    loop = asyncio.new_event_loop()
    backend = FileBackend("./db")
    scheduler = Scheduler(queue, loop, backend)
    try:
        loop.create_task(scheduler.run())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        if scheduler.tasks:
            drain = asyncio.wait_for(
                asyncio.gather(*scheduler.tasks),
                timeout=TIMEOUT,
            )
            loop.run_until_complete(drain)
    logger.info(f"Stopping SAJE worker [{os.getpid()}]. Goodbye")


class Runner:
    def __init__(self, workers=1) -> None:
        logger.info(f"Initializing SAJE with {workers=}")
        self.queue: Queue[str] = Queue()
        self.workers = [
            Process(
                target=manage,
                args=(self.queue,),
            )
            for _ in range(workers)
        ]

    def start(self):
        for worker in self.workers:
            worker.start()

    def stop(self):
        self.send(STOP)
        for worker in self.workers:
            worker.join()
            worker.close()

    def send(self, message):
        if not isinstance(message, str):
            message = json.dumps(message)
        self.queue.put_nowait(message)
