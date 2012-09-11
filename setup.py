#!/usr/bin/python

from setuptools import setup, find_packages


setup(name='mempeek', version='1.0.0',
    description='Memory Peek Middleware', author='Racklabs',
    url='https://swift.racklabs.com/', packages=find_packages(),
    classifiers=['Development Status :: 4 - Beta',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Environment :: No Input/Output (Daemon)'],
    entry_points={'paste.filter_factory': ['mempeek=mempeek:filter_factory']})
