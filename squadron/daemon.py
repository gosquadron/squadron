import urllib2
import socket
from git import *
import os
from squadron import main
import time

def run(home_dir, gitrepo, hub="http://provehito.com:8081"):

    if(gitrepo == None):
        print "please pass a git repo to poll"
        exit(1)

    if not(os.path.exists(os.path.join(home_dir, ".git"))):
        repo = Repo.clone_from(gitrepro, home_dir)
    else:
        repo = Repo(home_dir)
    

    if(hub == None or hub.find('http://') == -1):
        hub = "http://provehito.com:8081"
    url = (hub + "/register/" + str(socket.gethostname()))
    response = ':('
    try: 
        response = urllib2.urlopen(url).read()
    except:
        pass
    if(response == 'ok'):
        print "registered :)"
    else:
        print "could not register? :("

    lastCommit = ""
    while(True):
        
        repo.remote(name='origin').pull(refspec="refs/heads/master:refs/remotes/origin/master")
        currentCommit = repo.iter_commits().next()
        if(currentCommit != lastCommit):
            lastCommit = currentCommit
            print "updating node"
            try:
                main.apply(home_dir, socket.getfqdn())
            except:
                pass
        #Do heartbeat
        time.sleep(30)
