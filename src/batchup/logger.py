import logging
from typing import Any


class SimpleLogger:
    LEVEL_COLORS = {
        logging.DEBUG: "\033[35m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET = "\033[0m"

    def __init__(self, level: str = "INFO"):
        self.logger = logging.getLogger(name="SimpleLogger")
        self.set_level(level)
        handler = logging.StreamHandler()
        handler.setFormatter(self.ColoredFormatter())
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.propagate = False

    def set_level(self, level: str) -> None:
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    class ColoredFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            color = SimpleLogger.LEVEL_COLORS.get(record.levelno, "")
            reset = SimpleLogger.RESET
            level = f"{color}[{record.levelname}]{reset}"
            return f"{level} {record.getMessage()}"

    def write(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        print(f"{msg}")

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.critical(msg, *args, **kwargs)
