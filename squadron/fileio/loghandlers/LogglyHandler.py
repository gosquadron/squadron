import urllib2
import simplejson
import socket
from logging import Handler

class LogglyHandler(Handler):
    """
    Handler that logs to loggly.
    """
    base_url = None
    def __init__(self, base_url=None):
        if(base_url is None):
            self.base_url = 'https://logs-01.loggly.com/inputs/b121e4df-f910-4d6a-b6c1-b19ca2776233/tag/python/'
        else:
            self.base_url = base_url
        self.localip = socket.gethostbyname(socket.gethostname())
        self.publicip = urllib2.urlopen('http://ip.42.pl/raw').read()

    def emit(self, record):
        try:
            msg = record.getMessage()
            log_data = "PLAINTEXT=" + urllib2.quote(simplejson.dumps(
                {
                    'msg':msg,
                    'localip':self.localip,
                    'publicip':self.publicip,
                    'tenant':'TODO :)'
                }
            ))
            urllib2.urlopen(self.base_url, log_data)
        except(KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
