import logging
import sys
from .config import FILE_LOGGING


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        # Setup the telegram logger as a property
        self.telegram = logging.Logger(name + ".telegram", level)
        self._configure_loggers()

    def _configure_loggers(self):
        formatter = logging.Formatter(
            '************************************ %(levelname)s : %(filename)s : %(funcName)s() ************************************\n\n%(message)s\n\n')

        if FILE_LOGGING:
            # File handler
            file_handler = logging.FileHandler('app.log')
            file_handler.setFormatter(formatter)

            telegram_file_handler = logging.FileHandler('telegram.log')
            telegram_file_handler.setFormatter(formatter)

            self.addHandler(file_handler)
            self.telegram.addHandler(telegram_file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        self.addHandler(console_handler)
        self.telegram.addHandler(console_handler)


def setup_logger(name=__name__, level=logging.INFO):
    # Set our custom logger class
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    return logger


logger = setup_logger()
