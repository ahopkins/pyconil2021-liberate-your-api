import os
from log import logger
from multiprocessing import Queue, Process


class Scheduler:
    def __init__(self, queue) -> None:
        self.queue = queue


def manage(queue):
    logger.info(f"Saje running from {os.getpid()}")
    Scheduler(queue)


class Runner:
    def __init__(self) -> None:
        self.queue: Queue[str] = Queue()
        self.process = Process(target=manage, args=(self.queue,))

    def start(self):
        self.process.start()

    def stop(self):
        self.process.close()
