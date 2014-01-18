import git
import shutil
from extutils import get_filename
from template import render
import os

def ext_git(abs_source, dest, inputhash, loader, **kwargs):
    """ Clones a git repository """
    contents = render(abs_source, inputhash, loader).split()

    url = contents[0]
    if len(contents) > 1:
        refspec = contents[1]
    else:
        refspec = None

    finalfile = get_filename(dest)
    repo = git.Repo.clone_from(url, finalfile)

    if refspec:
        repo.git.checkout(refspec)

    return finalfile
