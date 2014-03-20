from squadron.notify import server, webhook
import bottle
import pytest
from webtest import TestApp, AppError
import threading
import time
import base64

def test_server():
    thread, serv = server.get_server('127.0.0.1', 34890, bottle.Bottle())
    thread.start()
    time.sleep(1)
    serv.stop()
    thread.join(2)
    assert not thread.isAlive()

def make_auth_header(username, password):
    return 'Basic ' + base64.b64encode(username + ':' + password)

def test_application():
    called = threading.Event()
    callback = lambda x: called.set()

    username = 'user'
    password = 'pass'

    wh = webhook.WebHookHandler(username, password, callback, None)
    app = TestApp(wh.application)

    resp = app.post_json('/', {'head_commit':{'commit':'id'}},
            headers={'Authorization':make_auth_header(username,password)})

    assert resp.status_int == 200
    assert resp.normal_body == 'OK'
    assert called.is_set()

    called.clear()

    with pytest.raises(AppError) as ex:
        resp = app.post_json('/', {'head_commit':{'commit':'id'}})
    assert not called.is_set()

    called.clear()

    with pytest.raises(AppError) as ex:
        resp = app.post_json('/', {'broken':True},
            headers={'Authorization':make_auth_header(username,password)})
    assert not called.is_set()
