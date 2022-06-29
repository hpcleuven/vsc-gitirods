from gitirods.util import getRepo, projectExists
from gitirods.project import createProjectCol
from gitirods.check_point import executeCheckPoint


def main():
    """
    Main function:
    Checks the git commits and if it recognizes an initial commit
    then creates a collection in iRODS for the repository name
    otherwise executes the check point function
    """
   
    try:
        repo, _ = getRepo()
        repo.commit('HEAD~1')
        if projectExists(repo):
            createProjectCol()
    except Exception as err:
        if err.args == ("Invalid revision spec 'HEAD~1^0' - not enough parent commits to reach '~1'",):
            createProjectCol()
        else:
            raise
    else:
        executeCheckPoint()
