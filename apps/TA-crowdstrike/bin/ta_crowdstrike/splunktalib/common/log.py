"""
Copyright (C) 2005-2015 Splunk Inc. All Rights Reserved.

log utility for TA
"""

import logging
import logging.handlers as handlers
import os.path as op
from splunktalib.splunk_platform import make_splunkhome_path
import splunktalib.common.util as cutil
from splunktalib.common.pattern import singleton

import time
logging.Formatter.converter = time.gmtime


def log_enter_exit(logger):
    """
    Log decorator to log function enter and exit
    """
    def log_decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug("{} entered.".format(func.__name__))
            result = func(*args, **kwargs)
            logger.debug("{} exited.".format(func.__name__))
            return result
        return wrapper
    return log_decorator


@singleton
class Logs(object):

    def __init__(self, namespace=None, default_level=logging.INFO):
        self._loggers = {}
        self._default_level = default_level
        if namespace is None:
            namespace = cutil.get_appname_from_path(op.abspath(__file__))

        if namespace:
            namespace = namespace.lower()
        self._namespace = namespace

    def get_logger(self, name, level=None,
                   maxBytes=25000000, backupCount=5):
        """
        Set up a default logger.

        :param name: The log file name.
        :param level: The logging level.
        :param maxBytes: The maximum log file size before rollover.
        :param backupCount: The number of log files to retain.
        """

        # Strip ".py" from the log file name if auto-generated by a script.
        if level is None:
            level = self._default_level

        name = self._get_log_name(name)
        if name in self._loggers:
            return self._loggers[name]

        logfile = make_splunkhome_path(["var", "log", "splunk", name])
        logger = logging.getLogger(name)

        handler_exists = any(
            [True for h in logger.handlers if h.baseFilename == logfile])
        if not handler_exists:
            file_handler = handlers.RotatingFileHandler(
                logfile, mode="a", maxBytes=maxBytes, backupCount=backupCount)

            formatter = logging.Formatter(
                "%(asctime)s +0000 log_level=%(levelname)s, pid=%(process)d, tid=%(threadName)s, "
                "file=%(filename)s, func_name=%(funcName)s, code_line_no=%(lineno)d | %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.setLevel(level)
            logger.propagate = False

        self._loggers[name] = logger
        return logger

    def set_level(self, level, name=None):
        """
        Change the log level of the logging

        :param level: the level of the logging to be setLevel
        :param name: the name of the logging to set, in case it is not set,
                     all the loggers will be affected
        """

        if name is not None:
            name = self._get_log_name(name)
            logger = self._loggers.get(name)
            if logger is not None:
                logger.setLevel(level)
        else:
            self._default_level = level
            for logger in self._loggers.itervalues():
                logger.setLevel(level)

    def _get_log_name(self, name):
        if name.endswith(".py"):
            name = name.replace(".py", "")

        if self._namespace:
            name = "{}_{}.log".format(self._namespace, name)
        else:
            name = "{}.log" .format(name)
        return name


# Global logger
logger = Logs().get_logger("util")


def reset_logger(name):
    """
    Reset global logger.
    """

    global logger
    logger = Logs().get_logger(name)
