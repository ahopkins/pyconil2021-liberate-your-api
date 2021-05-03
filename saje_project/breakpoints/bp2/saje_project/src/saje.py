import os
import asyncio
from queue import Empty
from log import logger
from multiprocessing import Queue, Process

STOP = "__STOP__"


class Scheduler:
    def __init__(self, queue) -> None:
        self.queue = queue

    async def run(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.consumer)

    def consumer(
        self,
    ):
        logger.info("Start consuming")
        while True:
            logger.info("> consuming")
            try:
                job = self.queue.get(timeout=1)
            except Empty:
                continue

            if job == STOP:
                logger.info("Stop consuming")
                break

            logger.info(f"> {job=}")


def manage(queue):
    logger.info(f"Saje running from {os.getpid()}")
    scheduler = Scheduler(queue)
    asyncio.run(scheduler.run())


class Runner:
    def __init__(self) -> None:
        self.queue: Queue[str] = Queue()
        self.process = Process(target=manage, args=(self.queue,))

    def start(self):
        self.process.start()

    def stop(self):
        self.process.join()
        self.process.close()

    def send(self, task_name):
        self.queue.put_nowait(task_name)
