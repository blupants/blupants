import os
from setuptools import setup
from setuptools import find_packages


def _path(filename):  # noqa: N802
    return os.path.join(os.path.dirname(__file__), filename)


DEFAULT_NAME = "blupants"
DEFAULT_REQS = [
    "Adafruit_BBIO",
    "rcpy"
]

if os.path.exists(_path("pip-requirements.txt")):
    with open(_path("pip-requirements.txt")) as fp:
        reqs = fp.read().strip()
else:
    reqs = DEFAULT_REQS


setup(
    name=DEFAULT_NAME,
    version="1.0.0a1",
    module_name=DEFAULT_NAME,
    python_requires='>=3.4',
    author="BluPants",
    author_email="blupants.robot@gmail.com",
    description="BluPants client module. This module allows your robot to execute commands from the "
                "BluPants Coding Lab (https://blupants.org).",
    url="https://blupants.com",
    package_dir={"": "src/python"},
    packages=find_packages("src/python"),
    license="Apache-2.0",
    install_requires=reqs,
    include_package_data=True,
    scripts=[
        "bin/blupants"
    ]
)
