import git
import shutil
from extutils import get_filename
import os

def ext_git(abs_source, dest, **kwargs):
    """ Clones a git repository """
    with open(abs_source) as gitfile:
        url = gitfile.read().strip()

    finalfile = get_filename(dest)
    repo = git.Repo.clone_from(url, finalfile)
    # get rid of the .git dir
    shutil.rmtree(os.path.join(finalfile, '.git'))
    return finalfile
