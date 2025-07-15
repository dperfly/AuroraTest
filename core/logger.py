import os

import logging
from logging import handlers
from typing import Text
import colorlog
import time

from core.utils.path import log_path


class LogHandler:
    """ 日志打印封装"""
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, filename: Text, level: Text = "info", when: Text = "D",
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


now_time_day = time.strftime("%Y-%m-%d", time.localtime())
INFO = LogHandler(os.path.join(log_path(), f"info-{now_time_day}.log"), level='info')
ERROR = LogHandler(os.path.join(log_path(), f"error-{now_time_day}.log"), level='error')
WARNING = LogHandler(os.path.join(log_path(), f"warning-{now_time_day}.log"))
