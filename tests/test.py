import unittest
import os
import pathlib
import glob
import subprocess
import shutil
import configparser
import time
from datetime import datetime
from git import Repo
from gitirods.iinit.session import SimpleiRODSSession
from irods.models import Collection
from irods.meta import iRODSMeta, AVUOperation
from gitirods.iinit.iinit import getIrodsSession
from gitirods.util import getRepo
from gitirods.project import touch
from gitirods.check_point import uploadArchive


def testConfigReader():
    """
    ConfigParser function
    Reads configuration variables inside the test config file
    and returns a reader object.
    Returns
    -------
    config : object
    """

    config_file = os.path.expandvars('$HOME/.config/test_gitirods.conf')
    config = config = configparser.ConfigParser()
    config.read(config_file)
    return config


def testRepo(repository_name, remoteurl=None):
    """
    Test Repo clone function
    Clones a test repo to the specified local directory
    Returns
    -------
    True
    """

    local_directory = os.path.expandvars(f'$HOME/{repository_name}')
    Repo.clone_from(remoteurl, local_directory)
    os.chdir(local_directory)
    return


def decideExternalRepo(path):
    """
    External Repo function
    Creates .repos file regardless of user input
    """

    external_repository = input("Are you using external repositories? [type anything] ")
    external_repository = 'Y'
    if external_repository == 'Y':
            touch(f'{path}/.repos')


def checkPointHelper(session, checkPointPath, repository_path):
    """
    Helper function
    In a simple way tries to mimic a repository operations.
    """

    attribute, value = ('checkPoint_test_attr', 'checkPoint_test_value')
    coll = session.collections.get(checkPointPath)
    coll.metadata.add(attribute, value)
    out_dir = 'out'
    out_dir_sub = 'subOut'
    out_file = 'test.txt'
    subOut_file = 'test1.txt'
    out_path = os.path.join(repository_path, out_dir)
    os.mkdir(out_path)
    out_sub_path = os.path.join(out_path, out_dir_sub)
    os.mkdir(out_sub_path)
    touch(out_path + '/' + out_file)
    touch(out_sub_path + '/' + subOut_file)
    touch(repository_path + '/' + 'program_test.py')


def iputCollection(sourcePath, destPath):
    """
    Upload function
    Upload the out* directories' local files and/or folders to the iRODS,
    in a manner that resembles the iCommands 'iput -r' command.
    """

    def walkRecursive(repo_path):
        """
        A generator function:
        Yields local root directory path and/or local files path.
        Differs from the orginal by [4:]
        """
        for root, _, files in os.walk(repo_path):
            local_dir = root.split(os.sep)[4:]
            local_dir_path = '/'.join(local_dir)
            yield local_dir_path
            for name in files:
                local_files_path = os.path.join(root, name)
                yield local_files_path
    out_dirs = glob.glob(sourcePath + '/out*')
    for item in out_dirs:
        for path in walkRecursive(item):
            if os.path.isdir(path):
                target_coll = os.path.join(destPath, path)
                with SimpleiRODSSession() as session:
                    session.collections.create(target_coll)
            elif os.path.isfile(path):
                file_name = os.path.basename(path)
                with SimpleiRODSSession() as session:
                    session.data_objects.put(path, target_coll + '/' + file_name)


class Testgitirods(unittest.TestCase):

    def setUp(self):
        config = testConfigReader()
        data = config.items("DEFAULT")
        repository_name = data[0][1]
        remoteurl = data[1][1]
        self.repository_name = repository_name
        self.remoteurl = remoteurl

    def test_01_renewIrodsSession_no_environment_file(self):
        """
        Tests iRODS session renewal for the case that the
        environment.json file has not been creatd yet.
        """

        env_file = os.path.expanduser('~/.irods/irods_environment.json')
        exist = os.path.exists(env_file)
        if not self.assertTrue(exist):
            getIrodsSession(3)
            cmd = ['iexit', 'full']
            subprocess.run(cmd)
            time.sleep(5)

    def test_02_renewIrodsSession_no_password(self):
        """
        Tests iRODS session renewal for the case that there
        is no valid user password.
        """

        with SimpleiRODSSession() as session:
            try:
                assert session.collections.exists(f'/{session.zone}/home/{session.username}')
            except Exception:
                getIrodsSession(3)

    def test_03_createProjectCol(self):
        """
        Tests createProjectCol function that exists in project.py
        in a lighter way.
        """

        repository_name = self.repository_name
        remoteurl = self.remoteurl
        testRepo(repository_name, remoteurl)
        _, repository_path = getRepo()
        with SimpleiRODSSession() as session:
            query = session.query(Collection)
            zone_name = session.zone
            user_name = session.username
            user_name = user_name.strip()
            collection_path = f'/{zone_name}/home/{user_name}/repositories/{repository_name}'
            result = query.filter(Collection.name == collection_path)
            try:
                if list(result) == []:
                    assert True
                    project_name = repository_name
                    session.collections.create(collection_path)
                    collection = session.collections.get(collection_path)
                    collection.metadata.apply_atomic_operations(
                        AVUOperation(operation='add',
                                    avu=iRODSMeta('user.git.hooks.project_name',
                                                f'{project_name}')))
                    touch(f'{repository_path}/.gitignore')
                    touch(f'{repository_path}/README.md')
                    decideExternalRepo(repository_path)
            except Exception as error:
                print(error)
        with SimpleiRODSSession() as session:
            self.assertEqual(session.collections.exists(collection_path), True)
            col = session.metadata.get(Collection, collection_path)
            self.assertEqual(col[0].name, 'user.git.hooks.project_name')
            self.assertEqual(col[0].value, f'{repository_name}')
            self.assertTrue(os.path.exists(f'{repository_path}/README.md'))
            self.assertTrue(os.path.exists(f'{repository_path}/.gitignore'))
            self.assertTrue(os.path.exists(f'{repository_path}/.repos'))

    def test_04_createCheckPoint(self):
        """
        Tests createCheckPoint function that exists in check_point.py
        in a similar way of how that function works.
        """
        _, repository_path = getRepo()
        repositoryName = pathlib.PurePath(repository_path).name
        with SimpleiRODSSession() as session:
            zone_name = session.zone
            user_name = session.username
            user_name = user_name.strip()
            query = session.query(Collection)
            query_filter = query.filter(Collection.name == f'/{zone_name}/home/{user_name}/repositories')
            irods_path_list = [item[Collection.name] for item in query_filter]
            irodsPath = irods_path_list[0] + '/' + repositoryName
            checkPointInput = input('Write your Checkpoint name: ')
            checkPointInput = checkPointInput.upper()
            checkPointNameExtension = datetime.today().strftime('%Y%m%d_%H%M')
            checkPointName = f'{checkPointInput}-{checkPointNameExtension}'
            checkPointPath = irodsPath + '/' + checkPointName
        with SimpleiRODSSession() as session:
            session.collections.create(checkPointPath)
            checkPointHelper(session, checkPointPath, repository_path)
            self.assertEqual(session.collections.exists(checkPointPath), True)
            col = session.metadata.get(Collection, checkPointPath)
            self.assertEqual(col[0].name, 'checkPoint_test_attr')
            self.assertEqual(col[0].value, 'checkPoint_test_value')
        iputCollection(repository_path, checkPointPath)
        cmd = ["git", "commit", "--allow-empty", "-m", "'Test Commit'"]
        subprocess.run(cmd)
        uploadArchive(repository_path, checkPointPath)
        with SimpleiRODSSession() as session:
            self.assertEqual(session.collections.exists(checkPointPath + '/out'), True)
            self.assertEqual(session.data_objects.exists(checkPointPath + '/archive.zip'), True)
        shutil.rmtree(repository_path)


if __name__ == '__main__':
    unittest.main()
