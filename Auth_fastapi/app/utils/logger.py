from pathlib import Path

from loguru import logger
import sys
import logging
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format ="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
)
log_path = project_root / "logs" / "app.log"
logger.add(
   log_path,
    level="DEBUG",
    rotation= "1 month",
    retention = "6 month",
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Пробрасываем логи в loguru, учитывая стек вызова для корректного отображения источника
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

# Подменяем хендлеры у популярных логгеров fastapi и uvicorn
for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(logger_name).handlers = [InterceptHandler()]