import threading
from cherrypy import wsgiserver

def get_server(address, port, application):
    def _serve(server):
        server.start()
    server = wsgiserver.CherryPyWSGIServer((address, int(port)), application)
    t = threading.Thread(target=_serve, args=(server,))
    t.daemon = True
    return (t, server)

