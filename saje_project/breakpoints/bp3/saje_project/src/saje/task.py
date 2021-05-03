from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Type

from .log import logger


class Task(ABC):
    __registry__: Dict[str, Type[Task]] = {}
    name = ""

    def __init_subclass__(cls) -> None:
        cls.__registry__[cls.name] = cls

    @abstractmethod
    async def run(self, **_):
        raise NotImplementedError


class HelloWorld(Task):
    name = "hello"

    async def run(self, name: str = "world", **_):
        for i in range(5):
            logger.info(f"> {str(i).rjust(2)}) Hello, {name}.")
            await asyncio.sleep(1)
