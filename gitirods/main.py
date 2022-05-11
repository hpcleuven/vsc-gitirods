from gitirods.util import getRepo
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
        repo.head.reference.commit
    except Exception as err:
        if err.args == ("Reference at 'refs/heads/master' does not exist",):
            createProjectCol()
        else:
            raise
    else:
        executeCheckPoint()
