from ConfigParser import SafeConfigParser, NoSectionError
import sys
import socket
import os
from ..exceptions import UserException
import logging
import logging.handlers
from time import strftime
from loghandlers import LogglyHandler
from singleton import singleton

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

@singleton
class SquadronConfig:

    def __init__(self):
        self._config_file = None
        self._defaults = None
        self._log = None
        self._loaded_parser = None
        self._initialized = False
        self._parsed_config = None

    #Only called by tests
    def _reset(self):
        self._initialized = False
        self._loaded_parser = None
        self._parsed_config = None
        self._log.handlers = []

    #This is not the constructor for a reason
    #It's hard to mix the singleton with a static method
    #TODO: Research a better way 
    def initialize(self, log, config_file, defaults = CONFIG_DEFAULTS()):
        """
        Loads the config, parses it and sets up logging
        """
#There is a bug when we start caching things.
#Comment this out when it's fixed
#        if(self._initialized):
#            return
        self._config_file = config_file
        self._defaults = defaults
        self._log = log
        self._initialized = True

    def get_config(self):
        """
        Gets the system config for squadron, and then caches it.
        """
        #TODO: handle race conditions with a lock
        if not self._initialized:
            raise Exception("Must call initialize in SquadronConfig once")

        #TODO: Actually cache it, there is a bug at the moment
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
        


    def parse_config(self):
        """
        Parses a given config file using SafeConfigParser. If the specified
        config_file is None, it searches in the usual places. Returns a
        dictionary of config keys to their values.
    
        """
        parser = self.get_config()

        if parser.sections():
            self._log.debug("Original section squadron: %s", parser.items('squadron'))
            result = self._defaults.copy()
            for section in CONFIG_SECTIONS:
                try:
                    result.update(parser.items(section))
                except NoSectionError:
                    pass
            return result
        else:
            raise _log_throw(self._log, 'No config file could be loaded. Make sure at least one of these exists and can be parsed: %s', CONFIG_PATHS)


    def parse_log_config(self):
        """
        Parses the config file for the log handlers
        """
        VALID_LOG_HANDLERS = set(['file', 'stream', 'rotatingfile', 'loggly'])
        VALID_STREAMS = set(['stdout', 'stderr'])
        log = self._log
        
        parser = self.get_config()
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
    
def parse_log_config(log, config_file):
    """
    Temporary function to not break existing code
    """
    global_config = SquadronConfig()
    global_config.initialize(log, config_file, defaults = CONFIG_DEFAULTS())
    global_config.parse_log_config()

def parse_config(log, config_file = None, defaults = CONFIG_DEFAULTS()):
    """
    Temporary function to not break existing code
    """
    global_config = SquadronConfig()
    global_config.initialize(log, config_file, defaults)
    return global_config.parse_config()

def _log_throw(log, error, *args):
    log.error(error, *args)
    raise UserException(error)
