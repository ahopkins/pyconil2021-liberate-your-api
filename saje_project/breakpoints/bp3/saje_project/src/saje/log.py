import logging

YELLOW = "\033[01;33m"


class SajeFormatter(logging.Formatter):
    def format(self, record):
        formatter = logging.Formatter(self._fmt, self.datefmt)
        return formatter.format(record)


logger = logging.getLogger("saje")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(
    SajeFormatter(
        fmt=(f"{YELLOW}%(asctime)s [%(process)d] [%(levelname)s] %(message)s\033[0m"),
        datefmt="[%Y-%m-%d %H:%M:%S %z]",
    )
)
logger.addHandler(ch)
