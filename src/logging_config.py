"""Structured JSON logging configuration using structlog.

Configures structlog and Python stdlib logging to emit JSON logs to stdout,
suitable for use with Docker logging systems such as Dozzle.

Usage::

    import logging_config

    logging_config.configure_logging()
    logger = logging_config.get_logger(__name__)
    logger.info("Something happened", key="value")
"""

import logging
import sys

import structlog


def configure_logging() -> None:
    """Configure structlog and Python stdlib logging to emit JSON structured logs.

    Logs are written to stdout in JSON format with the following fields:

    - ``timestamp``: ISO 8601 UTC timestamp (e.g. ``2026-03-06T10:30:12Z``)
    - ``level``: log level string (e.g. ``info``, ``warning``, ``error``)
    - ``event``: the log message
    - any extra keyword arguments passed to the logger call

    Designed to work with Docker logging systems such as Dozzle.
    """
    # Configure Python stdlib logging to write plain messages to stdout.
    # structlog's JSONRenderer produces the final JSON string, so the stdlib
    # handler only needs to emit the pre-formatted message as-is.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
        force=True,
    )

    structlog.configure(
        processors=[
            # Adds the ``level`` key (e.g. "info", "warning").
            structlog.stdlib.add_log_level,
            # Adds ``timestamp`` in ISO 8601 UTC format.
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            # Renders stack info if present.
            structlog.processors.StackInfoRenderer(),
            # Formats exception info into the event dict if present.
            structlog.processors.format_exc_info,
            # Ensures all string values are valid unicode.
            structlog.processors.UnicodeDecoder(),
            # Serialises the entire event dict to a JSON string.
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(*args):
    """Return a structlog logger instance.

    :param args: optional logger name (typically ``__name__``).
    :returns: a bound structlog logger.

    Example::

        logger = get_logger(__name__)
        logger.info("Todo retrieved", todo_id=5)
    """
    return structlog.get_logger(*args)
