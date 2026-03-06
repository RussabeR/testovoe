import logging

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)  # Можно INFO, WARNING, ERROR и т.д.

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
