import os
import ssl
from irods.session import iRODSSession
from gitirods.iinit.iinit import getIrodsSession
from gitirods.util import configReader


class SimpleiRODSSession(iRODSSession):
    """
    SimpleiRODSSession class is used to get an easy session
    by using the iRODSSession class from python-irodsclient.
    Example:
    with SimpleiRODSSession() as session:
        pass
    """

    def __init__(self):
        try:
            env_file = os.environ['IRODS_ENVIRONMENT_FILE']
        except KeyError:
            env_file = os.path.expanduser('~/.irods/irods_environment.json')
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
        ssl_settings = {'ssl_context': ssl_context}
        iRODSSession.__init__(self, irods_env_file=env_file, **ssl_settings)


def renewIrodsSession():
    """
    iRODS password renewal function:
    Checks the active iRODS session, if the session is expired, it executes
    getIrodsSession function in order to renew the password.
    """

    config = configReader()
    data = config.items("DEFAULT")
    zone_name = data[0][1]
    # Check if there is environment file exists
    env_file = os.path.expanduser('~/.irods/irods_environment.json')
    if not os.path.exists(env_file):
        getIrodsSession()
    else:
        with SimpleiRODSSession() as session:
            # Catch if no user or password exists
            try:
                session.collections.get(f'/{zone_name}/home/{session.username}')
                print('You have already a valid iRODS session.')
            except Exception:
                getIrodsSession()
