from gettext import install

# Setup file

from setuptools import setup

setup(
    name='Covid19 Dashboard',
    version='1.0',
    description='Covid19 Dashboard project for ECM1400',
    author='Kelly Blanca Irahola Vallejos',
    author_email='kbi201@exeter.ac.uk',
    url='http://127.0.0.1:5000/index',
    packages=['Flask','uk_covid19'],
)