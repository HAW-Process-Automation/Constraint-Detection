[![N|Solid](https://github.com/LeaTiedemann/Constraint-Detection/blob/main/HAW_Seeq.png)](https://www.seeq.com)

[![N|Scheme](https://github.com/LeaTiedemann/Constraint-Detection/blob/main/treemap_use_case_1.PNG)](https://constraint-detection.readthedocs.io/en/latest/index.html)

**seeq-constraintdetection** is an Add-on for control loop performance monitoring. It is used to find time periods when a control signal is constrained or saturated. This means that the signal is at its minimum or maximum and only 
deviates from there for short time periods. Control signals include all signals which are related to a control loop: Controller output (OP), setpoint (SP), process variable (PV), manipulated variable (MV) and auto-manual mode. 
Saturation occurs in the OP whereas constraints occur in the PV and MV due to their physical limitations (e.g. measuring range, actuator range) or in the SP (e.g. when model predictive control is applied). The Constraint Detection 
Add-on analyses the OP, SP, PV and MV and and generates a worksheet in treemap view where every controller panel is coloured according to the time-percentage a signal is constrained/saturated in the analysis time period.

# Documentation
[Documentation for **seeq-constraintdetection**](https://constraint-detection.readthedocs.io/en/latest/index.html)

# User Guide
[**seeq-constraintdetection** User Guide](https://constraint-detection.readthedocs.io/en/latest/userguide.html) provides an explanation of the required asset tree structure and the workflow in the user interface. The video below gives an introduction about the Constraint Detection Add-on.

https://user-images.githubusercontent.com/111488243/192772896-1b0b19a9-c70c-4486-994b-a8a13f5eb830.mp4

# Installation
The backend of **seeq-constraintdetection** requires **Python 3.7** or later.

## Dependencies
See [`requirements.txt`](https://github.com/HAW-Process-Automation/Constraint-Detection/blob/main/requirements.txt) file for a list of dependencies and versions. Additionally, you will need to install the `seeq` module with the appropriate version that matches your Seeq server. For more information on the `seeq` module see [seeq at pypi](https://pypi.org/project/seeq/).

## User Installation Requirements (Seeq Data Lab)
If you want to install **seeq-constraintdetection** as a Seeq Add-on, you will need:

* Seeq Data Lab (>=R54.1.6 or >=R56.1.4)
* `seeq` module whose version matches the Seeq server version
* Seeq administrator access
* Enable Add-on in the Seeq server

## User Installation (Seeq Data Lab)
The latest build of the project can be found [here](https://pypi.org/project/seeq-constraintdetection/) as a wheel file. The file is published as a courtesy and does not imply any guarantee or obligation for support from the publisher.

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-constraintdetection`
3. Run `python -m seeq.addons.constraintdetection`
4. Follow the instructions when prompted. ("Username or Access Key" is what you use to log in to Seeq. "Password" is your password for logging into Seeq.)

There are additional **Options** for the Add-on installation. These include `--users` and `--groups`. These can be used to change permissions for the Add-on Tool.
```
python -m seeq.addons.constraintdetection [--users <users_list> --groups <groups_list>]
```
# Development
We welcome new contributors of all experience levels. The Development Guide has detailed information about contributing code, documentation, tests, etc.

## Important links

* Official source code repo: [https://github.com/HAW-Process-Automation/Constraint-Detection](https://github.com/HAW-Process-Automation/Constraint-Detection)
* Issue tracker: [https://github.com/HAW-Process-Automation/Constraint-Detection/issues](https://github.com/HAW-Process-Automation/Constraint-Detection/issues)

## Source code
You can get started by cloning the repository with the command: 
```
git clone git@github.com:HAW-Process-Automation/seeq-constraintdetection.git
```

## Installation from source
For development work, it is highly recommended creating a python virtual environment and install the package in that working environment. If you are not familiar with python virtual environments, you can take a look [here](https://docs.python.org/3.8/tutorial/venv.html).

Once your virtual environment is activated, you can install requirements and **seeq-constraintdetection** from source with:
```
pip install -r requirements.txt
python setup.py install
```

# Support

Code related issues (e.g. bugs, feature requests) can be created in the [issue tracker](https://github.com/HAW-Process-Automation/Constraint-Detection/issues).


Maintainer: Lea Tiedemann

# Citation

Please cite this work as:
```
seeq-constraintdetection v0.0.3
Seeq Corporation, 2022
https://github.com/HAW-Process-Automation/Constraint-Detection
```
