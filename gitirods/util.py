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


def addAtomicMetadata(
        obj, keys, values,
        external_repos=None, func=None):
    """
    Metadata add function:
    It adds metadata (keys and values) atomically - transactionally in a single call - on
    an irods object
    Parameters
    ----------
    obj : an iRODS object (col=session.collections.get('path/to/collection'))
    keys : python list of attributes
    values : python list of values for attributes
    external_repos : python string for .repos path (default is None)
    func : python function that will return metedata keys and values
    from external repositories - defineExternalReposMetadata(path) (default is None)
    """

    if external_repos is None:
        avus = list(zip(keys, values))
        obj.metadata.apply_atomic_operations(*[AVUOperation(operation='add', \
                                             avu=iRODSMeta(meta[0], meta[1])) for meta in avus])
    else:
        if os.path.exists(external_repos):
            try:
                repository_path = os.path.dirname(external_repos)
                metadata = func(repository_path)
                external_attrs = list(metadata.keys())
                external_vals = list(metadata.values())
                all_attrs = keys + external_attrs
                all_values = values + external_vals
                avus = list(zip(all_attrs, all_values))
                obj.metadata.apply_atomic_operations(*[AVUOperation(operation='add', \
                                                     avu=iRODSMeta(meta[0], meta[1])) for meta in avus])
            except Exception as error:
                print(error)
        else:
            avus = list(zip(keys, values))
            obj.metadata.apply_atomic_operations(*[AVUOperation(operation='add', \
                                             avu=iRODSMeta(meta[0], meta[1])) for meta in avus])


def projectExists(object):
    """
    Check function:
    Based on a specific commit message it will determine whether
    the project in question exists or not.
    Parameters
    ----------
    object : instantiation of Repo
    Returns
    -------
    True : shows this is a nonempty repository
    """

    project_message = 'iRODS:Trigger project workflow'
    commits_list = list(object.iter_commits())
    commit_messages_list = []
    for item in range(len(commits_list)):
        commit = commits_list[item]
        commit_message = commit.message.strip()
        commit_messages_list.append(commit_message)
    if project_message not in commit_messages_list:
        return True
