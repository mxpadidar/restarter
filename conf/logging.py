"""Loguru configuration and request logging context."""

import logging
import pathlib
import sys

from loguru import logger

from conf.request_ctx import get_request_id


class InterceptHandler(logging.Handler):
    """Forward standard-library records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # RequestLoggingMiddleware owns 4xx access logs. Django emits a second
        # django.request record for the same response, so avoid duplicating it.
        if record.name == "django.request" and getattr(record, "status_code", 500) < 500:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        request_id = get_request_id()
        target = logger.bind(request_id=request_id) if request_id else logger
        target.opt(exception=record.exc_info, depth=6).log(
            level,
            record.getMessage(),
        )


def setup_logging(log_dir: pathlib.Path, level: str, diagnose: bool = False) -> None:
    """Configure Loguru sinks and redirect standard logging.

    :param log_dir: Directory for the structured JSON log file.
    :param log_level: Minimum level emitted by both sinks.
    :param diagnose: Include local variables in exception tracebacks.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()

    logger.add(
        sys.stdout,
        level=level,
        format=(
            "<level>{level:<8} | {time:YYYY-MM-DD HH:mm:ss!UTC}Z | {module} | {message}</level>"
        ),
        enqueue=True,
        backtrace=True,
        diagnose=diagnose,
    )
    logger.add(
        log_dir / "app.jsonl",
        level=level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        serialize=True,
        enqueue=True,
        backtrace=True,
        diagnose=diagnose,
    )

    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=level,
        force=True,
    )

    # RequestLoggingMiddleware is the single source of HTTP access logs.
    server_logger = logging.getLogger("django.server")
    server_logger.setLevel(logging.CRITICAL)
    server_logger.propagate = False
