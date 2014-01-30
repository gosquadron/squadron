from mock import MagicMock
import requests
from squadron import status
import ssl
import uuid
import hmac
import hashlib
import json

def test_basic():
    session = requests.session()
    session.mount = MagicMock()
    session.post = MagicMock()
    response = requests.Response()
    response.raise_for_status = MagicMock()
    session.post.return_value = response

    url = 'example.com'
    apikey = 'notarealkey'
    secret = 'e50ab0839519c9c2c7766e0cd40727c9ebbcdae90921025610da122007d3d924'
    nonce = str(uuid.uuid4())
    data = {'data':False}
    status.report_status(session, url, apikey, secret, nonce, True, **data)

    mount_point, adapter = session.mount.call_args[0]
    assert session.mount.called
    assert mount_point == 'https://'
    assert isinstance(adapter, status.SSLAdapter)

    hash_result = hmac.new(secret.decode('hex'), nonce, hashlib.sha256).hexdigest()
    result_url = '/'.join(['https:/', url, 'update',apikey, hash_result])
    session.post.assert_called_once_with(result_url, data=json.dumps(data),
            headers={
                'Content-Type':'application/json',
                'X-Nonce':nonce},
            verify=True)
    response.raise_for_status.assert_called_once_with()
