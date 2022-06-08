import os
import configparser
from irods.meta import iRODSMeta, AVUOperation
from git import Repo


def configReader():
    """
    ConfigParser function
    Reads configuration variables inside a file and returns a reader object.
    Returns
    -------
    config : object
    """

    config_file = os.path.expandvars('$HOME/.config/gitirods.conf')
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


def addAtomicMetadata(obj, keys, values):
    """
    Metadata add function:
    It adds metadata (keys and values) atomically - transactionally in a single call - on
    an irods object
    Parameters
    ----------
    obj : an iRODS object (col=session.collections.get('path/to/collection'))
    keys : python list fot attributes
    values : python list of values for attributes
    """

    avus = list(zip(keys, values))
    obj.metadata.apply_atomic_operations(*[AVUOperation(operation='add', \
                                         avu=iRODSMeta(meta[0], meta[1])) for meta in avus])
