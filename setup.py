#!/usr/bin/env python

from distutils.core import setup

setup(name='fusefs-cloudstorage',
        version='0.1',
        description='FUSE-based filesystem for accessing cloud storage such as Rackspace CloudFiles and Amazon S3',
        author='Roman Bogorodskiy',
        author_email='bogorodskiy@gmail.com',
        url='https://github.com/novel/fusefs-cloudstorage',
        scripts=['cloudstorage.py',],
        )

