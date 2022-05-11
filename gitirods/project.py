import os
import sys
import pathlib
from datetime import datetime
from irods.models import Collection
from irods.meta import iRODSMeta, AVUOperation
from gitirods.iinit.session import renewIrodsSession
from gitirods.iinit.session import SimpleiRODSSession
from gitirods.util import getRepo, configReader


def decideExternalRepo(path):
    """
    External Repo identifier function:
    Based on users' reply, this fucntion decides to create '.repos' file.
    Parameters
    ----------
    path : directoy/file
    Returns
    -------
    decideExternalRepo(path) or True/False : Bolean
    """

    external_repository = input("Are you using external repositories? [yes/Y or no/N] ")
    external_repository = external_repository.upper()
    external_repository = external_repository.replace('YES', 'Y')
    external_repository = external_repository.replace('NO', 'N')
    try:
        if external_repository == 'Y':
            touch(f'{path}/.repos')
            return True
        elif external_repository == 'N':
            print('You are not using external repositories.')
            return False
        else:
            print('Invalid Input')
            return decideExternalRepo(path)
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return decideExternalRepo(path)


def touch(path):
    """
    File create function:
    It creates an empty file given name,
    like what 'touch' command does in unix.
    Parameters
    ----------
    path : directoy/file.
    """

    with open(path, 'a'):
        os.utime(path, None)


def defineMetadataForProjectCol():
    """
    Metadata constructor function:
    Specifies metadata that will be added on the project collection
    based on user inputs and time.
    Returns
    -------
    project_name, project_description, humanReadableTime: str
    """

    project_name = input('Please name your project: ')
    project_description = input('Please describe the project [should not be longer than 280 characters!]: ')
    timestamp = round(datetime.timestamp(datetime.now()))
    date_time = datetime.fromtimestamp(timestamp)
    humanReadableTime = date_time.strftime('%d %B %Y - %H:%M')
    return project_name, project_description, humanReadableTime


def createProjectCol(group_name=None):
    """
    iRODS project creator function:
    Checks whether the name of a clonned git repository exists
    in the iRODS project home collection. Accordingly it creates
    a project(repository) collection inside the project home collection.
    Creates gitignore and README files. Once specified it also creates
    .repos file for external repositories.
    """

    renewIrodsSession()
    if group_name is None:
        config = configReader()
        data = config.items("DEFAULT")
        group_name = data[1][1]
    # Get the path of the repository in which this script is executed.
    repo, repository_path = getRepo()
    master = repo.head.reference
    committerName = master.commit.author.name
    committerMail = master.commit.author.email
    projectRepoURL = repo.remotes.origin.url
    repository_name = pathlib.PurePath(repository_path).name
    # Check whether the git repository name already exists or not
    with SimpleiRODSSession() as session:
        query = session.query(Collection)
        zone_name = session.zone
        collection_path = f'/{zone_name}/home/{group_name}/repositories/{repository_name}'
        result = query.filter(Collection.name == collection_path)
        try:
            if list(result) == []:
                project_name, project_description, \
                    humanReadableTime = defineMetadataForProjectCol()
                session.collections.create(collection_path)
                collection = session.collections.get(collection_path)
                # Add user enterred metadata on \
                # the project(repository name) collection
                project_owner = session.username
                collection.metadata.apply_atomic_operations(
                    AVUOperation(operation='add',
                                 avu=iRODSMeta('user.git.hooks.project_name',
                                               f'{project_name}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta('user.git.hooks.\
                                               project_description',
                                               f'{project_description}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta('user.git.hooks.project_owner',
                                               f'{project_owner}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta('user.git.hooks.\
                                               project_start_time',
                                               f'{humanReadableTime}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta(f'user.git.hooks.\
                                               project_repository_url',
                                               f'{projectRepoURL}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta(f'user.git.hooks.\
                                               project_repository_committer_name',
                                               f'{committerName}')),
                    AVUOperation(operation='add',
                                 avu=iRODSMeta(f'user.git.hooks.\
                                               project_repository_commit_mail',
                                               f'{committerMail}'))
                                                            )
                # Create .gittignore and README files in the clonned empty repository
                touch(f'{repository_path}/.gitignore')
                touch(f'{repository_path}/README.md')
                # In the case that external repositories are used the file .repos is created
                decideExternalRepo(repository_path)
                print('Completed!')
        except Exception as error:
            print(error)
            print(f'{error} wants to exit!')
            sys.exit()
