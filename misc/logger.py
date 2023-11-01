import logging
import os
import re
import sys
from copy import copy
from logging.handlers import RotatingFileHandler

from misc.colors import Colors


class Logger(logging.Logger):
    DIR = "/".join(__file__.split("/")[:-2])

    class Levels:
        DEBUG = 10
        INFO = 20
        WARN = 30
        ERROR = 40
        CRITICAL = 50
        PLAIN = 60

    def info_green(self, msg: str, *args, **kwargs):
        module, function = self.__get_module_and_function()
        self.info(msg, *args, **kwargs, extra={'col_start': Colors.COL.GREEN, 'crt_module': module, 'crt_func_name': function})

    def info_color(self, msg: str, color: str, *args, **kwargs):
        module, function = self.__get_module_and_function()
        self.info(msg, *args, **kwargs, extra={'col_start': color, 'crt_module': module, 'crt_func_name': function})

    def start_execution(self, message: str = None):
        module, function = self.__get_module_and_function()
        message = message if message is not None else "Execution started"
        self.info(message, extra={'col_start': Colors.COL.GREEN, 'crt_module': module, 'crt_func_name': function})

    def end_execution(self, success: bool = None):
        module, function = self.__get_module_and_function()
        color = Colors.COL.DEFAULT if success is None else Colors.COL.GREEN if success else Colors.COL.RED
        self.info("Execution ended.\n\n", extra={'col_start': color, 'crt_module': module, 'crt_func_name': function})

    def plain(self, msg: str, color: str = None, end: str = os.linesep, *args, **kwargs):
        if self.isEnabledFor(Logger.Levels.PLAIN):
            module, function = self.__get_module_and_function()
            extra = {'crt_module': module, 'crt_func_name': function, 'line_sep': end}
            if color is not None:
                extra['col_start'] = color
            self._log(Logger.Levels.PLAIN, msg, args, **kwargs, extra=extra)

    def __get_module_and_function(self) -> [str, str]:
        module, _, function, _ = self.findCaller(False, 3)
        module = module.split("/")[-1].split(".")[0]
        return module, function

    @staticmethod
    def init_logger(level: int, terminator: str = "", file_name: str = None, file_terminator: str = "", log_dir_offset: str = None, logs_path: str = None) -> "Logger":
        logger = Logger("VaultBackup")
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setFormatter(Formatter())
        ch.setLevel(level)
        ch.terminator = terminator
        logger.addHandler(ch)

        if file_name:
            if not logs_path:
                logs_path = Logger.DIR
            if log_dir_offset:
                logs_path = "/".join(logs_path.split("/") + [log_dir_offset])
            if not os.path.isdir("/".join(logs_path) if isinstance(logs_path, list) else logs_path):
                os.mkdir(logs_path)
            file_name = f"{logs_path}/{file_name}"
            fh = RotatingFileHandler(filename=file_name, mode="a", encoding='utf-8', backupCount=5, maxBytes=1024 ** 2 * 5)
            fh.setFormatter(FileFormatter())
            fh.setLevel(level)
            fh.terminator = file_terminator
            logger.addHandler(fh)
        return logger


class LevelData:
    def __init__(self, label: str, color: str, text_format: str):
        self.label = label
        self.color = color
        self.text_format = text_format


class FileFormatter(logging.Formatter):
    LINE_SEP = "\n"
    logging.addLevelName(Logger.Levels.PLAIN, "PLAIN")
    FORMATS = {
        Logger.Levels.DEBUG: LevelData("DEBUG", Colors.COL.GREY, "%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
        Logger.Levels.INFO: LevelData("INFO", Colors.COL.DEFAULT, "%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
        Logger.Levels.WARN: LevelData("WARN", Colors.COL.YELLOW, "%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
        Logger.Levels.ERROR: LevelData("ERROR", Colors.COL.RED, "%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
        Logger.Levels.CRITICAL: LevelData("CRITICAL", Colors.COL.PURE.RED, "%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
        Logger.Levels.PLAIN: LevelData("PLAIN", Colors.COL.DEFAULT, "%(col_start)s%(message)s%(col_end)s%(terminator)s")
    }

    def format(self, message) -> str:
        cpy_msg = copy(message)
        level_data = self.FORMATS.get(cpy_msg.levelno)
        cpy_msg.level_name = level_data.label
        if hasattr(cpy_msg, 'crt_module'):
            cpy_msg.module = cpy_msg.crt_module
        if hasattr(cpy_msg, 'crt_func_name'):
            cpy_msg.funcName = cpy_msg.crt_func_name
        cpy_msg.terminator = cpy_msg.line_sep if hasattr(cpy_msg, 'line_sep') else self.LINE_SEP
        self.custom_format(cpy_msg, level_data)
        return logging.Formatter(level_data.text_format).format(cpy_msg)

    def custom_format(self, cpy_message, level_data) -> None:
        cpy_message.col_start = ''
        cpy_message.col_end = ''
        # Remove colors and \r
        cpy_message.msg = re.sub(r"\r|\\033\[\d+m|\\033\[[34]8;(\d+;){3}\d+m", "", cpy_message.msg)


class Formatter(FileFormatter):
    def custom_format(self, cpy_message, level_data) -> None:
        cpy_message.col_end = Colors.END
        if not hasattr(cpy_message, 'col_start'):
            cpy_message.col_start = level_data.color


enable_file_logging = False
LOGGER = Logger.init_logger(Logger.Levels.INFO, file_name="backup.log" if enable_file_logging else None)
LOGGER_TEST = LOGGER.init_logger(Logger.Levels.DEBUG)
