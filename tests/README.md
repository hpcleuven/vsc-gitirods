# vsc-gitirods - test

The test.py uses [test config file](test_gitirods.conf) in addition to the gitirods.conf file. Therefore you should also create `$HOME/.config/test_gitirods.conf` file on your local pc.
After that, you will need to edit both config files according to your test zone information. The test module will create project collection inside the 'repositories' collection under your use home collection .

Your pyhton version should be at least 3.7 or newer.

To run the test module;

After you clone this repository, run the `python tests/test.py` command in your terminal. Check the results to see 'Ok'.

You will have to see two times iRODS session renewal. Also, you will see a project collection and a check point collection in iRODS together with some metadata attached.
