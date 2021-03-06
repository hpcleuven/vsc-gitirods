# vsc-gitirods

The goal of this project is to help researchers in the logging of their research-milestones in iRODS. These milestones, or checkpoints, are decided by researchers once they reach to some meaningful output for their research using a git repository. Then, a computational experiment output together with some metadata attached and a snapshot of all codes and inputs used to generate those results should automatically and instantly be stored in iRODS.

To this end, vsc-gitirods offers an integrated workflow triggered by the post-commit hook in order to upload checkpoints in iRODS. 

## How to use

- Set up a virtual environment, this is not a must but highly recommended.
- Install vsc-gitirods. This will also automatically install other required libraries such as python-irodsclient and GitPython. Thus, you do not need to install another iRODS client, i.e. iCommands, to get an active iRODS session.
- Create the `$HOME/.config/gitirods.conf` file on your local pc, copy the content of [this](gitirods.conf) link and update the default values according to your own zone information and group name.
- Depending on your project/need, you can either create a remote empty git repository and clone this repository on your local pc or use an already existing repository,
- Configure your git repository hook by following instructions below:
    * Go to the directory where your repository in question is located; `cd <cloned-repository-name>`,
    * Create a post-commit hook file by using your favorite text editor or command; `touch .git/hooks/post-commit`,
    * Copy the code snippet below and paste in the post-commit file you have just created,
    * Adjust the shebang line for your python environment if required.
    * Make your script file executable; `chmod +x .git/hooks/post-commit`
- Follow the equivalent steps of instructions given above for Windows machines,
- Execute `git commit --allow-empty -m "iRODS:Trigger project workflow"` to create project files and a corresponding iRODS collection. **It is required to use this unique git message as a first commit both in your empty or non-empty repositories as an initiator of your workflow.**.
- Once you give a positive answer to the 'Is a checkpoint reached?' question, the process for the checkpoint sync to iRODS will start.


The code snippet that will be stored in the post-commit file:

```python
#!/usr/bin/env python3

# A workaround against EOFError
import sys
sys.stdin = open('/dev/tty')

from gitirods.main import main

if __name__ == '__main__':
    main()
```


## Dependencies

- Python >= 3.7
- python-irodsclient <= v1.1.1
- GitPython 3.1.20 or newer
- Git 1.7.0 or newer

## Installation

If you have downloaded the source code:

    python setup.py install

or if you want to obtain a copy from the Pypi repository:

    pip install vsc-gitirods

## Uninstallation

    pip uninstall vsc-gitirods

Be aware this will not uninstall any dependencies.

## Limitations

- This package can work only for the Vlaams Supercomputing Centrum (VSC) and KU Leuven iRODS zones. The reason for this is that the iRODS authentication is being ensured by using an internal repository providing an API end point for authenticating the python-irodsclient (PRC) against iRODS.

- This workflow assumes projects collection (git repository names) will be created inside the 'repositories' collection that will be preferably created in advance in the group collection - `/tempZone/home/myGroup/repositories`.

- The design of this workflow is placed on some phases/changes on the master/main git branch. Therefore it may not work with other git branches other than `main` or `master` branch.

- Since the work-flow requires some user input (interactivity), this package can only work using git commands (`git commit`) in the command line, meaning it may not work properly if the `git commit` command is called on a graphical user interface.
