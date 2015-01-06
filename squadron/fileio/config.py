from ConfigParser import SafeConfigParser, NoSectionError
import sys
import socket
import os
from ..exceptions import UserException
import logging
import logging.handlers
from time import strftime
from loghandlers import LogglyHandler

def CONFIG_DEFAULTS():
    return {
        'polltime':'30',
        'keydir':'/etc/squadron/keydir',
        'nodename':socket.gethostname(),
        'statedir':'/var/squadron',
        'send_status': 'false',
    }

#This is not a func so that we can change it in a test
CONFIG_PATHS = ['/etc/squadron/config',
        '/usr/local/etc/squadron/config',
        os.path.expanduser('~/.squadron/config'),
        ]


CONFIG_SECTIONS = set(['squadron', 'status', 'daemon', 'webhook'])

LOG_FORMAT = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def log_file_parse(log, logline, level):
    if len(logline) < 3:
        raise _log_throw(log, 'File log handler needs output file as last parameter: %s', logline)

    param = logline[2]
    fh = logging.FileHandler(param, 'a', None, False)
    fh.setLevel(level)
    fh.setFormatter(LOG_FORMAT)

    # Send an event only to this logger so we know when it started since we append
    timestr = strftime("%Y-%m-%d %H:%M:%S")
    breaker = '========================================================='
    args = breaker, timestr, breaker
    record = logging.LogRecord('normal', 10, '', 0, '\n\n%s\nLogging started at %s\n%s\n', args, None) 
    fh.handle(record)
    return fh

def log_stream_parse(log, logline, level):
    VALID_STREAMS = set(['stdout', 'stderr'])
    if len(logline) < 3:
        raise _log_throw(log, 'File log handler needs stream such as sys.stderr as last parameter: %s', logline)
    param = logline[2].lower()
    if param not in VALID_STREAMS:
        raise _log_throw(log, 'Invalid stream param passed: %s', logline)

    if param == 'stdout':
        param = sys.stdout
    if param == 'stderr':
        param = sys.stderr

    sh = logging.StreamHandler(param)
    sh.setLevel(level)
    sh.setFormatter(LOG_FORMAT)
    return sh

def log_rotate_parse(log, logline, level):
    if len(logline) < 4:
        raise _log_throw(log, 'Rotating log handler needs a file name, max size and maxCount')

    rh = logging.handlers.RotatingFileHandler(logline[2], 'a', logline[3], logline[4])
    rh.setLevel(level)
    rh.setFormatter(LOG_FORMAT)
    return rh

def log_loggly_parse(log, logline, level):
    lg = None
    if len(logline) < 3:
        lg = LogglyHandler.LogglyHandler()
    else:
        lg = LogglyHandler.LogglyHandler(logline[3])
    lg.setLevel(level)
    lg.setFormatter(LOG_FORMAT)
    return lg

LOG_FUNC = {
    'file': log_file_parse,
    'stream': log_stream_parse,
    'rotatingfile': log_rotate_parse,
    'loggly': log_loggly_parse,
}

def parse_log_config(squadron_dir, log, config_file):
    """
    Parses the config file for the log handlers
    """
    parser = _get_config(squadron_dir, log, config_file)
    log.setLevel(10) #DO NOT REMOVE THIS LINE (Ideally this should be the lowest level logged)

    if 'log' in parser.sections():
        for _, value in parser.items('log'):
            logline = value.split()
            if len(logline) < 2:
                raise _log_throw(log, 'Invalid log config passed: %s', value)

            # parse level
            level_str = logline[0]
            level = getattr(logging, level_str.upper(), None)
            if not isinstance(level, int):
                raise _log_throw(log, 'Invalid log level passed for: %s', value)

            # parse handler
            handler = logline[1].lower()
            if handler in LOG_FUNC:
                log_handle = LOG_FUNC[handler](log, logline, level)
                log.addHandler(log_handle)
            else:
                raise _log_throw(log, 'Invalid log handler: %s', handler)


def _get_config(squadron_dir, log, config_file):
    parser = SafeConfigParser()
    if config_file:
        log.debug("Using config file: %s", config_file)
        with open(config_file) as cfile:
            parser.readfp(cfile, config_file)
    else:
        # Try defaults
        squadron_dir_config = os.path.join(squadron_dir, '.squadron', 'config')
        parsed_files = parser.read(CONFIG_PATHS + [squadron_dir_config])
        log.debug("Using config files: %s", parsed_files)
    return parser

def parse_config(squadron_dir, log, config_file = None,
        defaults = CONFIG_DEFAULTS()):
    """
    Parses a given config file using SafeConfigParser. If the specified
    config_file is None, it searches in the usual places. Returns a
    dictionary of config keys to their values.
    """
    parser = _get_config(squadron_dir, log, config_file)

    if parser.sections():
        log.debug("Original section squadron: %s", parser.items('squadron'))
        result = defaults.copy()
        for section in CONFIG_SECTIONS:
            try:
                result.update(parser.items(section))
            except NoSectionError:
                pass
        return result
    else:
        raise _log_throw(log, 'No config file could be loaded. Make sure at least one of these exists and can be parsed: %s', CONFIG_PATHS)

def _log_throw(log, error, *args):
    log.error(error, *args)
    raise UserException(error)
