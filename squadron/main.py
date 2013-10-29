import os
import git

def main():
    try:
        repo = git.Repo(os.getcwd())
        print repo.rev_parse('--show-toplevel')
    except git.exc.InvalidGitRepositoryError:
        print "Not a git repository"
