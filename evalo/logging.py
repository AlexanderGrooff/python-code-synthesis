import sys
import logging
import structlog


logging.basicConfig(
    format="%(message)s", stream=sys.stdout, level=logging.INFO
)
structlog.configure(
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
)
