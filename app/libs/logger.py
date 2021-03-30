import logging


class LoggerHandler(logging.Logger):
    def __init__(
        self, name="main", level="DEBUG", format="%(levelname)s:%(name)s:%(message)s"
    ):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        fmt = logging.Formatter(format)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)
        stream_handler.setFormatter(fmt)

        self.logger = logger

    def debug(self, msg):
        return self.logger.debug(msg)

    def info(self, msg):
        return self.logger.info(msg)

    def warning(self, msg):
        return self.logger.warning(msg)

    def error(self, msg):
        return self.logger.error(msg)
