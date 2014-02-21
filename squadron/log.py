import logging
import datetime
from fileio.config import parse_log_config
log = logging.getLogger('normal')

class SpecialFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG :"DEBUG: %(module)s: %(lineno)d: %(message)s",
               logging.INFO : "%(message)s",
               'DEFAULT' : "%(levelname)s: %(message)s"}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


def setup_log(loglevel, config_file=None, console=False):
    if console:
        level = getattr(logging, loglevel.upper(), None)
        if not isinstance(level, int):
            raise ValueError('Invalid log level {}'.format(loglevel))

        log.setLevel(level)

        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(SpecialFormatter())
        log.addHandler(ch)
    else:
        parse_log_config(log, config_file)

