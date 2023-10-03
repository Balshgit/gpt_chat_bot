import logging
import os
import sys
from types import FrameType
from typing import TYPE_CHECKING, Any, cast

import graypy
from loguru import logger
from sentry_sdk.integrations.logging import EventHandler

from constants import LogLevelEnum
from settings.config import DIR_LOGS, settings

if TYPE_CHECKING:
    from loguru import Record
else:
    Record = dict[str, Any]


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage().replace(settings.TELEGRAM_API_TOKEN, "TELEGRAM_API_TOKEN".center(24, "*")),
        )


def configure_logging(
    *, level: LogLevelEnum, enable_json_logs: bool, enable_sentry_logs: bool, log_to_file: str | None = None
) -> None:
    intercept_handler = InterceptHandler()

    formatter = _json_formatter if enable_json_logs else _text_formatter

    base_config_handlers = [intercept_handler]

    base_loguru_handler = {
        "level": level.name,
        "serialize": enable_json_logs,
        "format": formatter,
        "colorize": False,
    }
    loguru_handlers = [
        {**base_loguru_handler, "colorize": True, "sink": sys.stdout},
    ]

    if settings.GRAYLOG_HOST and settings.GRAYLOG_PORT:
        graylog_handler = graypy.GELFUDPHandler(settings.GRAYLOG_HOST, settings.GRAYLOG_PORT)
        base_config_handlers.append(graylog_handler)
        loguru_handlers.append({**base_loguru_handler, "sink": graylog_handler})
    if log_to_file:
        file_path = os.path.join(DIR_LOGS, log_to_file)
        if not os.path.exists(log_to_file):
            with open(file_path, 'w') as f:
                f.write('')
        loguru_handlers.append({**base_loguru_handler, "sink": file_path})

    logging.basicConfig(handlers=base_config_handlers, level=level.name)
    logger.configure(handlers=loguru_handlers)

    # sentry sdk не умеет из коробки работать с loguru, нужно добавлять хандлер
    # https://github.com/getsentry/sentry-python/issues/653#issuecomment-788854865
    # https://forum.sentry.io/t/changing-issue-title-when-logging-with-traceback/446
    if enable_sentry_logs:
        handler = EventHandler(level=logging.WARNING)
        logger.add(handler, diagnose=True, level=logging.WARNING, format=_sentry_formatter)


def _json_formatter(record: Record) -> str:
    # Обрезаем `\n` в конце логов, т.к. в json формате переносы не нужны
    return record.get("message", "").strip()


def _sentry_formatter(record: Record) -> str:
    return "{name}:{function} {message}"


def _text_formatter(record: Record) -> str:
    # WARNING !!!
    # Функция должна возвращать строку, которая содержит только шаблоны для форматирования.
    # Если в строку прокидывать значения из record (или еще откуда-либо),
    # то loguru может принять их за f-строки и попытается обработать, что приведет к ошибке.
    # Например, если нужно достать какое-то значение из поля extra, вместо того чтобы прокидывать его в строку формата,
    # нужно прокидывать подстроку вида {extra[тут_ключ]}

    # Стандартный формат loguru. Задается через env LOGURU_FORMAT
    format_ = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Добавляем мета параметры по типу user_id, art_id, которые передаются через logger.bind(...)
    extra = record["extra"]
    if extra:
        formatted = ", ".join(f"{key}" + "={extra[" + str(key) + "]}" for key, value in extra.items())
        format_ += f" - <cyan>{formatted}</cyan>"

    format_ += "\n"

    if record["exception"] is not None:
        format_ += "{exception}\n"

    return format_
