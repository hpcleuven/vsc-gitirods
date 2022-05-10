import os
from irods import exception
from git import Repo
from gitirods.iinit import SimpleiRODSSession, getIrodsSession
from irods.meta import iRODSMeta, AVUOperation
from irods.models import Collection
from gitirods.project import touch
from gitirods.util import getRepo


def test_renewIrodsSession():
    
    with SimpleiRODSSession() as session:
        assert not exception.CAT_INVALID_AUTHENTICATION == None
        getIrodsSession()
    return


def testRepo(repository_name, remoteurl=None):
    
    local_directory = os.path.expandvars(f'$HOME/{repository_name}')
    Repo.clone_from(remoteurl, local_directory)
    os.chdir(local_directory)
    return


def decideExternalRepo(path):
    external_repository = input("Are you using external \
                                 repositories? [yes/Y or no/N] ")
    assert external_repository == 'Y'
    if external_repository == 'Y':
            touch(f'{path}/.repos')


def test_createProjectCol(repository_name, group_name=None, remoteurl=None):

    testRepo(repository_name, remoteurl=None)
    _, repository_path = getRepo()
    with SimpleiRODSSession() as session:
        query = session.query(Collection)
        zone_name = session.zone
        collection_path = f'/{zone_name}/home/{group_name}\
                            /repositories/{repository_name}'
        result = query.filter(Collection.name == collection_path)
        assert list(result) == []
        try:
            if list(result) == []:
                project_name = repository_name
                session.collections.create(collection_path)
                collection = session.collections.get(collection_path)
                project_owner = session.username
                collection.metadata.apply_atomic_operations(
                    AVUOperation(operation='add',
                                avu=iRODSMeta('user.git.hooks.project_name',
                                            f'{project_name}')))
                touch(f'{repository_path}/.gitignore')
                touch(f'{repository_path}/README.md')
                decideExternalRepo(repository_path)
        except AssertionError:
            pass
        else:
            msg = 'Trying to create an already existing collection is expected '
            msg += 'to raise an AssertionError'
            raise RuntimeError(msg)


if __name__ == '__main__':
    test_renewIrodsSession()
    test_createProjectCol('numa', group_name='testGroup', remoteurl='git@github.com:mstfdkmn/numa.git')
