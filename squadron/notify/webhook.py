import bottle
from bottle import post, request, response, parse_auth
import json

class WebHookHandler:
    def __init__(self, username, password, callback, log):
        self.username = username
        self.password = password
        self.callback = callback
        self.log = log
        self.application = bottle.Bottle()
        self.application.route('/', method='POST', callback=self.handle)

    def _raise(self, code, message):
        if self.log:
            self.log.error('Returning %s: %s', code, message)
        raise bottle.HTTPError(code, message)

    def require_auth(fn):
        def check(self, *args, **kwargs):
            auth = request.get_header('Authorization')
            if auth:
                (user, password) = parse_auth(auth)
                if user == self.username and password == self.password:
                    return fn(self, *args, **kwargs)
            self._raise(401, 'Requires auth')

        return check

    @require_auth
    def handle(self):
        data = request.json

        if self.log:
            self.log.debug('Webhook push request: %s', data)

        if 'head_commit' in data:
            self.callback(data['head_commit'])
            return "OK"
        self._raise(400, 'Request didn\'t have head')
