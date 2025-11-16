from loguru import logger as loguru_logger
from typing import Optional


def get_logger(level: str = "INFO", log_file: Optional[str] = None):
    """

    :param level: уровень логирования
    :param log_file
    :return: объект loguru.logger
    """
    loguru_logger.remove()

    # Консольный лог
    loguru_logger.add(
        sink=lambda msg: print(msg, end=''),
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}"
    )

    # Файл логов, если указан
    if log_file:
        loguru_logger.add(
            log_file,
            level="DEBUG",
            rotation="10 MB",  # например, ротация каждые 10 МБ
            retention="7 days",  # хранить 7 дней
            compression="zip"
        )

    return loguru_logger
