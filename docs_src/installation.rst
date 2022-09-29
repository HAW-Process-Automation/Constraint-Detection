Installation
============

The backend of **seeq-constraintdetection** requires **Python 3.7** or later.

Dependencies
------------
See :code:`requirements.txt` file for a list of dependencies and versions. Additionally, you will need to install the :code:`seeq` module with the appropriate version that matches your Seeq server. For more information on the :code:`seeq`
module see `seeq at pypi <https://pypi.org/project/seeq/>`_.


User Installation Requirements (Seeq Data Lab)
----------------------------------------------
If you want to install **seeq-constraintdetection** as a Seeq Add-on Tool, you will need:

* Seeq Data Lab (>= R54.1.6 or >= R56.1.4)
* :code:`seeq` module whose version matches the Seeq server version
* Seeq administrator access
* Enable Add-on Tools in the Seeq server


User Installation (Seeq Data Lab)
---------------------------------
The latest build of the project can be found `here <https://pypi.org>`_ as a wheel file. The file is published as as courtesy and does not imply any guarantee or obligation for support from the publisher.

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run :code:`pip install constraintdetection`
3. Run :code:`python -m seeq.addons.constraintdetection`

Follow the instructions when prompted. ("Username or Access Key" is what you use to log in to Seeq. "Password" is your password for logging into Seeq.)

There are additional **Options** for the Add-on installation. These include :code:`--users` and :code:`--groups`. These can be used to change permissions for the Add-on Tool. ::

	python -m seeq.addons.constraintdetection [--users <users_list> --groups <groups_list>]

Installation from source
------------------------
You can get started by cloning the repository with the command: ::

	git clone git@github.com:HAW-Process-Automation/Constraint-Detection.git

For development work, it is highly recommended creating a python virtual environment and install the package in that working environment. If you are not familiar with python virtual environments, you can take a look `here <https://docs.python.org/3.8/tutorial/venv.html>`_.

Once your virtual environment is activated, you can install requirements and **seeq-constraintdetection** from source with: ::

	pip install -r requirements.txt
	python setup.py install





