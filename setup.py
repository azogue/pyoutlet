# -*- coding: utf-8 -*-
"""
Python Setup file

"""
from codecs import open
import os
from setuptools import setup, find_packages
from pyoutlet import __version__, basedir


packages = find_packages(exclude=['docs', '*tests*', 'notebooks'])
with open(os.path.join(basedir, '..', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyoutlet',
    version=__version__,
    description='Python CLI & Web switcher for Etekcity power outlets using 433MHz RF emitter',
    long_description='\n' + long_description,
    keywords='home-automation power outlet raspberry',
    author='Eugenio Panadero',
    author_email='azogue.lab@gmail.com',
    url='https://github.com/azogue/pyoutlet',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Topic :: Home Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Operating System :: Unix'],
    packages=packages,
    package_data={
        'pyoutlet': ['switch.sh', 'codes_outlets.json'],
        'pyoutletweb': ['templates/*', 'static/css/*'],
    },
    install_requires=['flask>=0.11'],
    entry_points={
        'console_scripts': [
            'switch = pyoutlet.__main__:main',
            'pyoutletweb = pyoutletweb.__init__:main_runweb'
        ]
    }
)
