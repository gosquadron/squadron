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
        'nodename':socket.getfqdn(),
        'statedir':'/var/squadron',
        'send_status': 'false',
    }

#This is not a func so that we can change it in a test
CONFIG_PATHS = ['/etc/squadron/config',
        '/usr/local/etc/squadron/config',
        os.path.expanduser('~/.squadron/config'),
        ]


CONFIG_SECTIONS = set(['squadron', 'status', 'daemon'])

#http://legacy.python.org/dev/peps/pep-0318/#examples
#TODO: move elsewhere
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class SquadronConfig:

    def __init__(self):
        self._config_file = None
        self._defaults = None
        self._log = None
        self._loaded_parser = None
        self._initialized = False

    #Only called by tests
    def _reset(self):
        self._initialized = False
        self._loaded_parser = None

    #This is not the constructor for a reason
    #It's hard to mix the singleton with a static method
    #TODO: Research a better way 
    def initialize(self, log, config_file, defaults):
        self._config_file = config_file
        self._defaults = defaults
        self._log = log
        self._initialized = True

    def get_config(self):
        #TODO: handle race conditions with a lock
        if not self._initialized:
            raise Exception("Must call initialize in SquadronConfig once")

        if self._loaded_parser is None:
            self._loaded_parser = SafeConfigParser()
    
        if self._config_file is None:
            # Try defaults
            parsed_files = self._loaded_parser.read(CONFIG_PATHS)
            self._log.debug("Using config files: %s", parsed_files)
        else:
            self._log.debug("Using config file: %s", self._config_file)
            with open(self._config_file) as cfile:
                self._loaded_parser.readfp(cfile, self._config_file)
        return self._loaded_parser

def parse_config(log, config_file = None, defaults = CONFIG_DEFAULTS()):
    """
    Parses a given config file using SafeConfigParser. If the specified
    config_file is None, it searches in the usual places. Returns a
    dictionary of config keys to their values.

    Keyword arguments:
        defaults -- the default global values for the config
        config_file -- the configuration file to read config from. If
            None, searches for system-wide configuration and from
            the local user's configuration.
    """
    global_config = SquadronConfig()
    global_config.initialize(log, config_file, defaults)
    parser = global_config.get_config()

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

def parse_log_config(log, config_file):
    VALID_LOG_HANDLERS = set(['file', 'stream', 'rotatingfile', 'loggly'])
    VALID_STREAMS = set(['stdout', 'stderr'])

    global_config = SquadronConfig()
    global_config.initialize(log, config_file, [])
    parser = global_config.get_config()
    log.setLevel(10) #DO NOT REMOVE THIS LINE (Ideally this should be the lowest level logged)
    if 'log' in parser.sections():
        for _, value in parser.items('log'):
            logline = value.split()
            print logline
            if len(logline) < 2:
                raise _log_throw(log, 'Invalid log config passed: %s', value)

            # parse level
            level_str = logline[0]
            level = getattr(logging, level_str.upper(), None)
            if not isinstance(level, int):
                raise _log_throw(log, 'Invalid log level passed for: %s', value)

            # parse handler
            handler = logline[1].lower()
            if handler not in VALID_LOG_HANDLERS:
                raise _log_throw(log, 'Invalid log handler passed for: %s', value)

            if handler == 'file':
                if len(logline) < 3:
                    raise _log_throw(log, 'File log handler needs output file as last parameter: %s', value)
                param = logline[2]
                fh = logging.FileHandler(param, 'a', None, False)
                fh.setLevel(level)
                
                #Send an event only to this logger so we know when it started since we append
                timestr = strftime("%Y-%m-%d %H:%M:%S")
                breaker = '========================================================='
                args = breaker, timestr, breaker
                record = logging.LogRecord('normal', 10, '', 0, '\n\n%s\nLogging started at %s\n%s\n', args, None) 
                fh.handle(record)

                log.addHandler(fh)

            if handler == 'stream':
                if len(logline) < 3:
                    raise _log_throw(log, 'File log handler needs stream such as sys.stderr as last parameter: %s', value)
                param = logline[2].lower()
                if param not in VALID_STREAMS:
                    raise _log_throw(log, 'Invalid stream param passed: %s', value)

                if param == 'stdout':
                    param = sys.stdout
                if param == 'stderr':
                    param = sys.stderr

                sh = logging.StreamHandler(param)
                sh.setLevel(level)
                log.addHandler(sh)

            if handler == 'rotatingfile':
                if len(logline) < 4:
                    raise _log_throw(log, 'Rotating log handler needs a file name, max size and maxCount')

                rh = logging.handlers.RotatingFileHandler(logline[2], 'a', logline[3], logline[4])
                rh.setLevel(level)
                log.addHandler(rh)
            if handler == 'loggly':
                lg = None
                if len(logline) < 3:
                    lg = LogglyHandler.LogglyHandler()
                else:
                    lg = LogglyHandler.LogglyHandler(logline[3])
                lg.setLevel(level)
                log.addHandler(lg)
                print 'setup loggly'

def _log_throw(log, error, *args):
    log.error(error, *args)
    raise UserException(error)
