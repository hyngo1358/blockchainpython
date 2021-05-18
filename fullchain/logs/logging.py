import logging
from typing import List, Optional, Tuple

from logzero import LogFormatter

Component = str
LogLevel = int
LogConfiguration = Tuple[Component, LogLevel]


class BlockAll(logging.Filter):
    def filter(self, record):
        # allow no records to pass through
        return False


class LogManager(object):
    loggers: dict = {}

    root = 'chain-python.'

    block_all_filter = BlockAll()

    def configStdio(self, log_configurations: Optional[List[LogConfiguration]] = None,
                    default_level=logging.INFO) -> None:
        """
        Configure the stdio `StreamHandler` levels on the specified loggers.
        If no log configurations are specified then the `default_level` will be applied to all handlers.
        Args:
            log_configurations: a list of (component name, log level) tuples
            default_level: logging level to apply when no log_configurations are specified
        """
        # no configuration specified, apply `default_level` to the stdio handler of all known loggers
        if not log_configurations:
            for logger in self.loggers.values():
                self._restrictOutput(logger, default_level)
        # only apply specified configuration to the stdio `StreamHandler` of the specific component
        else:
            for component, level in log_configurations:
                try:
                    logger = self.loggers[self.root + component]
                except KeyError:
                    raise ValueError("Failed to configure component. Invalid name: {}".format(component))
                self._restrictOutput(logger, level)

    def _restrictOutput(self, logger: logging.Logger, level: int) -> None:
        # we assume the first handler is always our STDIO handler
        if logger.hasHandlers():
            logger.handlers[0].setLevel(level)

    def muteStdio(self) -> None:
        """
        Intended to temporarily mute messages by applying a `BlockAll` filter.
        Use in combination with `muteStdio()`
        """

        for logger in self.loggers.values():
            if logger.hasHandlers():
                logger.handlers[0].addFilter(self.block_all_filter)

    def unmuteStdio(self) -> None:
        """
        Intended to re-store the temporarily disabled logging of `unmuteStdio()` by removing the `BlockAll` filter.
        """
        for logger in self.loggers.values():
            if logger.hasHandlers():
                logger.handlers[0].removeFilter(self.block_all_filter)

    def getLogger(self, component_name: str = None) -> logging.Logger:
        """
        Get the logger instance matching ``component_name`` or create a new one if non-existent.
        Args:
            component_name: a neo-python component name. e.g. network, vm, db
        Returns:
            a logger for the specified component.
        """
        logger_name = self.root + (component_name if component_name else 'generic')
        _logger = self.loggers.get(logger_name)
        if not _logger:
            _logger = logging.getLogger(logger_name)

            stdio_handler = logging.StreamHandler()
            stdio_handler.setFormatter(LogFormatter())
            stdio_handler.setLevel(logging.INFO)
            _logger.addHandler(stdio_handler)
            _logger.setLevel(logging.DEBUG)
            self.loggers[logger_name] = _logger
        return _logger


log_manager = LogManager()
