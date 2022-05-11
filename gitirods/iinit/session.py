import os
import ssl
from irods.session import iRODSSession
from gitirods.iinit.iinit import getIrodsSession


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

    with SimpleiRODSSession() as session:
        try:
            session.collections.get(f'/{session.zone}/home/{session.username}')
            print('You have already a valid iRODS session.')
        except Exception as error:
            # CAT_INVALID_AUTHENTICATION
            if error.code == -826000:
                getIrodsSession()
