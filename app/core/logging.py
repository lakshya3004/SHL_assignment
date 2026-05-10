import sys
import logging
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Standard logging handler to intercept standard logging messages and pass them to Loguru.
    This ensures that logs from libraries like FastAPI/Uvicorn are captured by Loguru.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """
    Configure Loguru as the primary logger and intercept standard logging.
    """
    # Remove default Loguru handler
    logger.remove()

    # Add custom handler for stdout
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Intercept standard logging (FastAPI, Uvicorn, etc.)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Silence some overly verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info("Logging system initialized.")
