from melogger import Colors
from melogger import LoggerBuilder, Levels

LOG = LoggerBuilder.get_logger("VaultBackup-Test", Levels.DEBUG)


def log_response(function) -> any:
    module, func_name = LOG.findCaller(False, 3)[0].split("/")[-1].split(".")[0], function.__name__
    # noinspection SpellCheckingInspection
    extra = {'crt_module': module, 'crt_func_name': func_name, 'line_sep': '\n', "col_start": Colors.COL.RED}

    # noinspection PyProtectedMember
    def execute(*args, **kwargs) -> None:
        try:
            function(*args, **kwargs)
            extra['col_start'] = Colors.COL.GREEN
        finally:
            if extra['col_start'] == Colors.COL.RED:
                LOG._log(40, f"Test '{function.__name__}' FAILED.", [], extra=extra)
            else:
                LOG._log(20, f"Test '{function.__name__}' finished SUCCESSFULLY.", [], extra=extra)

    return execute
