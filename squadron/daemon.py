import urllib2
import socket

def run(home_dir, gitrepro, hub="http://provehito.com:8081"):

    if(gitrepro == None):
        print "please pass a git repro to poll"
        exit(1)

    if(hub == None or hub.find('http://') == -1):
        hub = "http://provehito.com:8081"
    url = (hub + "/register/" + str(socket.gethostname()))
    print url
    response = urllib2.urlopen(url).read()
    if(response == 'ok'):
        print "registered :)"
    else:
        print "could not register? :("
    
