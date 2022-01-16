import logging.handlers
import platform

logger = logging.getLogger("vigilant_crypto_snatch")

if platform.system() == "Linux":
    h = logging.handlers.SysLogHandler(address="/dev/log")
    h.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    h.setLevel(logging.INFO)
    logger.addHandler(h)

__version__ = "5.4.2"
