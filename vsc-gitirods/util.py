import os
import configparser
from git import Repo


def configReader():
    """
    ConfigParser function
    Reads configuration variables inside a file and returns a reader object.
    Parameters
    ----------
    conf : Configuration file.
    Returns
    -------
    config : object
    """

    config_file = os.path.expandvars('$HOME/.config.conf')
    config = config = configparser.ConfigParser()
    config.read(config_file)
    return config


def getRepo(repository_path=None):
    """
    Object function:
    It instantiate the Repo object and returns it together with
    the repository path.
    Parameters
    ----------
    repository_path : None
    Returns
    -------
    repo : object
    repository_path : str
    """

    if repository_path is None:
        repository_path = os.getcwd()
    repo = Repo(repository_path)
    return repo, repository_path
