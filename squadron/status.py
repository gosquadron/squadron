import requests
import hmac
import hashlib
import uuid
import json
from log import log

from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import ssl

class SSLAdapter(HTTPAdapter):
    '''An HTTPS Transport Adapter that uses an arbitrary SSL version.'''
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=self.ssl_version)


def report_status(session, server, apikey, secret, nonce, verify, **kwargs):
    """
    Reports status via the HTTPS API. Given the server, API key and
    secret, this method generates the hash_result of a nonce.

    Pass hostname, status, and info in the kwargs. Raises an exception
    when a non-200 result code is returned.

    Keyword arguments:
        session -- a requests session object
        server -- The server to report status to. Can be host:port
        apikey -- The API key to use
        secret -- The API secret associated with this API key
        nonce -- a random string only to be used once
        verify -- Whether or not to verify the SSL connection
        hostname -- The hostname to identify this server by
        status -- OK or ERROR
        info -- Dictionary of more information
    """
    raw_secret = secret.decode('hex')

    hash_result = hmac.new(raw_secret, nonce, hashlib.sha256).hexdigest()

    log.debug("Got body: {}".format(kwargs))

    # Requests doesn't handle TLSv1 by default
    session.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))

    resp = session.post('https://{}/update/{}/{}'.format(server, apikey, hash_result),
                data=json.dumps(kwargs),
                headers={
                    'Content-Type':'application/json',
                    'X-Nonce':nonce},
                verify=verify)

    resp.raise_for_status()
