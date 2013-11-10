import urllib2
import socket

def run(home_dir, gitrepro, hub="http://provehito.com:8081"):

    if(gitrepro == None):
        print "please pass a git repro to poll"
        exit(1)

    repro = Repo.clone_from(gitrepro, home_dir)
    

    if(hub == None or hub.find('http://') == -1):
        hub = "http://provehito.com:8081"
    url = (hub + "/register/" + str(socket.gethostname()))
    print url
    response = urllib2.urlopen(url).read()
    if(response == 'ok'):
        print "registered :)"
    else:
        print "could not register? :("
    
    while(True):
        
        git.pull(refspec="refs/heads/master:refs/remotes/origin/master")
        print git.refs.master

