import os
import sys
import shutil
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

config_file_target_path = os.path.expanduser('~/.config')
if not os.path.exists(config_file_target_path):
    os.makedir(config_file_target_path)

def copyConfigFile():
    original = os.path.join(sys.prefix, 'gitirods.conf')
    target = os.path.join(config_file_target_path, 'gitirods.conf')
    shutil.copyfile(original, target)

setup_args = dict(
    name='vsc-gitirods',
    version='v0.1',
    description='git iRODS work flow integration tool in Python',
    long_description_content_type="text/markdown",
    long_description=README,
    license='LGPL-3.0 license',
    packages=find_packages(),
    data_files=[(sys.prefix, ['gitirods.conf'])],
    author='ICTS-RDM',
    author_email='mustafa.dikmen@kuleuven.be',
    keywords=['git', 'iRODS', 'gitirods', 'Python 3', 'GitPython'],
    url='https://github.com/hpcleuven/vsc-gitirods',
    download_url='https://pypi.org/project/vsc-gitirods/'
)

install_requires = [
    'python-irodsclient<=v1.1.1',
    'GitPython'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
    copyConfigFile()
