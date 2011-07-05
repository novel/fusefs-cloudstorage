#!/usr/bin/env python

import os
import sys
import shlex
import subprocess
import time

import libcloud.security
from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

import nose.tools as ntools

from secrets import driver, access_id, secret

libcloud.security.VERIFY_SSL_CERT = True

class TestFSOperations(object):
    MOUNT_POINT = "./test"

    MOUNT_CMD = "./cloudstorage.py -o driver=%(driver)s -o access_id=%(access_id)s -o secret=%(secret)s %(mpoint)s" % \
            {"driver": driver, "access_id": access_id, "secret": secret, "mpoint": MOUNT_POINT}
    UMOUNT_CMD = "umount ./test"

    def setup(self):
        print "mounting test filesystem"
        args = shlex.split(self.MOUNT_CMD)
        p = subprocess.Popen(args)
        p.wait()

        if 0 != p.returncode:
            print >>sys.stderr, "failed to mount filesystem"
            sys.exit(1)

        print "setting up libcloud storage connection"

        self.storage_handle = get_driver(getattr(Provider, driver))(access_id, secret)
        print self.storage_handle

    def teardown(self):
        print "umounting test filesystem"
        args = shlex.split(self.UMOUNT_CMD)
        p = subprocess.Popen(args)
        p.wait()

        if 0 != p.returncode:
            print >>sys.stderr, "failed to umount filesystem"
            sys.exit(1)

    def test_container_listing(self):
        actual = set(os.listdir(self.MOUNT_POINT))
        expected = set([str(cont.name) for cont in self.storage_handle.list_containers()])

        ntools.assert_equals(actual, expected)
