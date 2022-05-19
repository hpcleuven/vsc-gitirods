import os
import os.path
import sys
import socket
import json
import threading
import urllib.parse
import webbrowser
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from irods.session import iRODSSession
from irods.password_obfuscation import encode
from gitirods.util import configReader


def findFreePort():
    """
    Free port finder function:
    Finds a free port by binding a socket to a port
    selected by the operating system
    Returns
    -------
    port : int
    """

    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    return port


# Global variables
HOSTNAME = 'localhost'
SERVERPORT = findFreePort()


class PRCHandler(BaseHTTPRequestHandler):
    """
    An extension class to the BaseHTTPRequestHandler (a subclass of HTTPServer,
    socketserver.TCPServer).
    This is used to handle the request.
    Example:
    python -m http.server 8000
    """

    def do_GET(self):
        """
        GET function:
        Handle GET request. If the local web server is successfully enabled,
        PRCHandler.do_GET will be called.
        """
        # The request is mapped by interpreting the request as a path
        path = self.path[10:]
        # parse out query strings
        configAll = urllib.parse.parse_qsl(path, keep_blank_values=True)
        configRaw = dict([item for item in configAll if item[0] != 'password'])
        # Add uid for windows
        configRaw['authentication_uid'] = str(1000)
        # Add 'irods_' prefix that is needed for irods_environment.json
        prefix = 'irods_'
        config = {prefix + str(key): val for key, val in configRaw.items()}
        # Convert number values to integer as required by iRODS authentication
        for key, value in config.items():
            if value.isdigit():
                config[key] = int(value)
        config = json.dumps(config)
        # Exclude the password from the irods_environment.json
        passwordRaw = dict([item for item in configAll if item[0] == 'password'])
        password = passwordRaw.get('password')
        # Write some information on te redirected page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('<html><head><style>h1 {text-align: center;}</style>\
            <title>Python iRODS Client (PRC) on Windows</title></head>', 'utf-8'))
        self.wfile.write(bytes('<h1>Python iRODS Client (PRC) on Windows</h1>', 'utf-8'))
        self.wfile.write(bytes(f'<p><mark>CONFIG:</mark> {config}</p>', 'utf-8'))
        self.wfile.write(bytes(f'<p><mark>PASSWORD:</mark> {password}</p>', 'utf-8'))
        env_file = os.getenv('IRODS_ENVIRONMENT_FILE', os.path.expanduser('~/.irods/irods_environment.json'))
        self.wfile.write(bytes('<h3><i>You have successfully authenticated. Use iRODSSession(irods_env_file=' +
                               repr(env_file) + ') to start interacting with iRODS.</i></h3>', 'utf-8'))
        # Call 'iinit' function
        iinit(config, password)
        sys.exit()


def iinit(config, password):
    """
    iinit function:
    Equivalent of iCommands' iinit command.
    Creates irods_environment.json, which contains a set of key-value pairs defining iRODS configuration.
    Also creates file(.irodsA) containing your iRODS password in a obfuscated form (server sends back).
    """

    def write(file, contents):
        """
        A write function to create a file
        """
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(contents)
    env_file = os.getenv('IRODS_ENVIRONMENT_FILE', os.path.expanduser('~/.irods/irods_environment.json'))
    write(env_file, config)
    with iRODSSession(irods_env_file=env_file, password=password) as session:
        write(iRODSSession.get_irods_password_file(), encode(session.pam_pw_negotiated[0], uid=1000))
        print(' ')
        print('You have successfully authenticated. Use iRODSSession(irods_env_file=' +
              repr(env_file) + ') to start interacting with iRODS.')


def openCallback(port=SERVERPORT):
    """
    Webbrowser open function:
    Opens the redirected URL on a defaut browser (callback of the go portal)
    """

    config = configReader()
    data = config.items("DEFAULT")
    zone_host_name = data[0][1]
    webbrowser.open(f'https://{zone_host_name}/auth/iinit?redirect_uri=http://{HOSTNAME}:{port}/callback')


def run(server_class=HTTPServer, handler_class=PRCHandler, host=HOSTNAME, port=SERVERPORT):
    """
    Run fucntion:
    Setting up a localhost webserver
    Sets up the HTTP server and start it in a separate daemon thread
    """

    server_address = (host, port)
    localServer = server_class(server_address, handler_class)
    thread = threading.Thread(target=localServer.serve_forever)
    thread.daemon = True
    thread.start()
    print('  ', sep='\n')
    print(f'Starting local server on {host}:{port}')


def down(server_class=HTTPServer, handler_class=PRCHandler, host=HOSTNAME, port=SERVERPORT):
    """
    Stop function:
    Shuts down the HTTP server
    """

    server_address = (host, port)
    localServer = server_class(server_address, handler_class)
    threading.Thread(target=localServer.shutdown())
    print(f'Shutting down local server on {host}:{port}')


def getIrodsSession(wait=None):
    """
    Activation fucntion:
    In order to renew iRODS session, it executes other relavant
    functions in order.
    """

    openCallback()
    # if the run time for the server is too long, it quits the program
    try:
        run()
    except KeyboardInterrupt:
        down()
    # wait until the local webserver finished starting up
    if wait == None:
        time.sleep(20)
    else:
        time.sleep(wait)
