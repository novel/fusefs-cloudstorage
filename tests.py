#!/usr/bin/env python

import os
import os.path
import sys
import shlex
import subprocess
import time
import uuid

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

    _dirs_to_cleanup = []
    _files_to_cleanup = []

    @staticmethod
    def setup_class():
        print "CLASS SETUP"

    @staticmethod
    def teardown_class():
        print "CLASS TEARDOWN"

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
        """container listing"""

        actual = set(os.listdir(self.MOUNT_POINT))
        expected = set([str(cont.name) for cont in self.storage_handle.list_containers()])

        ntools.assert_equals(actual, expected)

    def test_container_creation_and_removal(self):
        """container creation and removal"""

        container_name = str(uuid.uuid1()).replace("-", "")
        container_path = os.path.join(self.MOUNT_POINT, container_name)

        self._dirs_to_cleanup.append(container_name)
        os.mkdir(container_path)

        ntools.assert_true(container_name in [str(cont.name) for cont in self.storage_handle.list_containers()])

        os.rmdir(container_path)

    @ntools.nottest
    def test_file_io(self):
        """file I/O"""

        content = """hello world\n
this is fusefs-cloudstorage speaking!\n
bebebe"""

        container_name = str(uuid.uuid1()).replace("-", "")
        container_path = os.path.join(self.MOUNT_POINT, container_name)
        object_name = "test_file.txt"
        object_path = os.path.join(container_path, object_name)

        self._dirs_to_cleanup.append(container_name)
        os.mkdir(container_path)

        fd = open(object_path, "w")
        fd.write(content)
        fd.close()

        fd = open(object_path)
        read_content = fd.read()

        import shutil
        shutil.rmtree(container_path)
        #os.unlink(object_path)
        #os.rmdir(container_path)

        ntools.assert_equals(content, read_content)
