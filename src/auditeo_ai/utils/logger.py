import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

# --- Context Variables (Global State) ---
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")
ip_address_ctx: ContextVar[str] = ContextVar("ip_address", default="-")


# --- Custom Wrapper ---
class TraceReturningLogger:
    """
    Wraps a standard logger to return the Trace ID after logging.
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
        return correlation_id_ctx.get()

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
        return correlation_id_ctx.get()

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
        return correlation_id_ctx.get()

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)
        return correlation_id_ctx.get()


# --- Configuration ---
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get()
        record.ip_address = ip_address_ctx.get()
        return True


def get_logger(name: str = "app") -> TraceReturningLogger:
    """
    Returns the custom wrapper that enables: trace_id = logger.error(...)
    """
    # 1. Get the standard Python logger
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s %(ip_address)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
        handler.setFormatter(formatter)

        # Add Filter
        context_filter = ContextFilter()
        logger.addFilter(context_filter)
        logger.addHandler(handler)

    return TraceReturningLogger(logger)
