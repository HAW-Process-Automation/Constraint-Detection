import re
from parver import Version, ParseError
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version_scope = {'__builtins__': None}
with open("seeq/addons/constraintdetection/_version.py", "r+") as f:
    version_file = f.read()
    version_line = re.search(r"__version__ = (.*)", version_file)
    if version_line is None:
        raise ValueError(f"Invalid version. Expected __version__ = 'xx.xx.xx', but got \n{version_file}")
    version = version_line.group(1).replace(" ", "").strip('\n').strip("'").strip('"')
    print(f"version: {version}")
    try:
        Version.parse(version)
        exec(version_line.group(0), version_scope)
    except ParseError as e:
        print(str(e))
        raise

setup_args = dict(
    name='seeq-constraintdetection',
    version=version_scope['__version__'],
    author="Lea Tiedemann",
    author_email="lea.tiedemann@seeq.com",
    license="Apache License 2.0",
    platforms=["Linux", "Windows"],
    description="Constraint and saturation detection in control loop data in Seeq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HAW-Process-Automation/Constraint-Detection",
    packages=setuptools.find_namespace_packages(include=['seeq.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ipyvuetify>=1.8.2',
        'numpy>=1.20.1',
        'pandas>=1.2.4',
        'pytz~=2021.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

setuptools.setup(**setup_args)