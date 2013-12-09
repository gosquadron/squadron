import requests
import hmac
import hashlib
import uuid

def report_status(server, apikey, secret, verify, **kwargs):
    """
    Reports status via the HTTPS API. Given the server, API key and
    secret, this method generates the hash_result of a nonce.

    Pass hostname, status, and info in the kwargs. Raises an exception
    when a non-200 result code is returned.

    Keyword arguments:
        server -- The server to report status to. Can be host:port
        apikey -- The API key to use
        secret -- The API secret associated with this API key
        verify -- Whether or not to verify the SSL connection
        hostname -- The hostname to identify this server by
        status -- OK or ERROR
        info -- Dictionary of more information
    """
    raw_secret = secret.decode('hex')
    nonce = str(uuid.uuid4())

    hash_result = hmac.new(secret, nonce, hashlib.sha256).hexdigest()

    resp = requests.post('https://{}/update/{}/{}'.format(server, apikey, hash_result),
                params=kwargs, headers={'X-Nonce':nonce}, verify=verify)

    resp.raise_for_status()
