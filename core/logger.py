import os
import time
from datetime import datetime

import logging
from logging import handlers
from typing import Text, Any
import colorlog

from core.model import TestCaseRunResult, ReportLogEntry
from core.utils.path import log_path

now_time_day = time.strftime("%Y-%m-%d", time.localtime())

class LogHandler:
    """ 日志打印封装"""
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, filename: Text, test_run_result: TestCaseRunResult = None, level: Text = "info",
                 when: Text = "D",
                 fmt: Text = "%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s"):
        self.logger = logging.getLogger(filename)
        formatter = self.log_color()
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        screen_output = logging.StreamHandler()
        screen_output.setFormatter(formatter)
        time_rotating = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=3, encoding='utf-8')
        time_rotating.setFormatter(format_str)
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
        self.log_path = os.path.join(log_path(), "log.log")
        self.test_run_result = test_run_result

    @classmethod
    def log_color(cls):
        """ 设置日志颜色 """
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config
        )
        return formatter

INFO  = LogHandler(os.path.join(log_path(), f"info-{now_time_day}.log"), level='info')
WARNING = LogHandler(os.path.join(log_path(), f"warning-{now_time_day}.log"))
ERROR = LogHandler(os.path.join(log_path(), f"error-{now_time_day}.log"), level='error')

def info_log(text: Any, test_run_result: TestCaseRunResult = None):
    INFO.logger.info(str(text))
    if test_run_result:
        test_run_result.logs.append(
            ReportLogEntry(time=datetime.now().isoformat(), level='info',
                           message=str(text))
        )


def error_log(text: Any, test_run_result: TestCaseRunResult = None):
    ERROR.logger.error(str(text))
    if test_run_result:
        test_run_result.logs.append(
            ReportLogEntry(time=datetime.now().isoformat(), level='error',
                           message=str(text))
        )


def warring_log(text: Any, test_run_result: TestCaseRunResult = None):
    WARNING.logger.warning(str(text))
    if test_run_result:
        test_run_result.logs.append(
            ReportLogEntry(time=datetime.now().isoformat(), level='warring',
                           message=str(text))
        )
