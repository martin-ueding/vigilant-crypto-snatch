import logging
import logging.handlers

logger = logging.getLogger("vigilant_crypto_snatch")

h = logging.handlers.SysLogHandler(address="/dev/log")
h.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
logger.addHandler(h)

__version__ = "4.2.2"
