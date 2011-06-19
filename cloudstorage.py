#!/usr/bin/env python

import os
import sys
import stat
import errno
import logging

try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse

from libcloud.storage.types import (Provider,
        ContainerDoesNotExistError, ObjectDoesNotExistError)
from libcloud.storage.providers import get_driver

fuse.fuse_python_api = (0, 2)


class CloudStat(fuse.Stat):

    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class CloudStorageFS(fuse.Fuse):
    _storage_handle = None

    def __init__(self, *args, **kwargs):
        fuse.Fuse.__init__(self, *args, **kwargs)

        logging.basicConfig(filename='storage.log', level=logging.DEBUG)
        logging.debug("Starting CloudStorageFS")

    @property
    def storage_handle(self):
        if not self._storage_handle:
            CloudFiles = get_driver(getattr(Provider, self.driver))

            self._storage_handle = CloudFiles(self.access_id, self.secret)

        return self._storage_handle

    def _read_container_names(self):
        return [container.name for container in
                self.storage_handle.list_containers()]

    def getattr(self, path):
        logging.debug("getattr(path='%s')" % path)

        st = CloudStat()

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
            return st

        path_tokens = path.split('/')

        if 2 == len(path_tokens):
            container_names = self._read_container_names()

            if path_tokens[1] in container_names:
                st.st_mode = stat.S_IFDIR | 0755
                st.st_nlink = 2
                return st
            else:
                return -errno.ENOENT
        elif 3 == len(path_tokens):
            container_name, object_name = path_tokens[1], path_tokens[2]
            obj = self.storage_handle.get_object(container_name, object_name)
            
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = obj.size
            return st

        return -errno.ENOENT

    def readdir(self, path, offset):
        logging.debug("readdir(path='%s', offset='%s')" % (path, offset))

        if "/" == path:
            try:
                container_names = [str(container.name) for container in
                    self.storage_handle.list_containers()]

                logging.debug("container names = %s" % container_names)
                dirs = [".", ".."] + container_names

                logging.debug("dirs = %s" % dirs)

                for r in  dirs:
                    logging.debug("yielding %s" % r)
                    yield fuse.Direntry(r)
                #return dirs
            except Exception:
                logging.exception("exception in readdir()")
        else:
            path_tokens = path.split("/")

            if 2 != len(path_tokens):
                # we should only have 1 level depth
                logging.warning("Path '%s' is deeper than it should" % path)
                return

            try:
                container_name = path_tokens[1]
                container = self.storage_handle.get_container(container_name)
                dirs = [".", ".."] +  [str(obj.name) for obj in container.list_objects()]

                logging.debug("dirs = %s" % dirs)

                for r in dirs:
                    yield fuse.Direntry(r)
            except Exception:
                logging.exception("exception while trying to list container objects")

    def mkdir(self, path, mode):
        logging.debug("mkdir(path='%s', mode='%s')" % (path, mode))

        path_tokens = path.split('/')
        if 2 != len(path_tokens):
            logging.warning("attempting to create a non-container dir %s" % path)
            return -errno.EOPNOTSUPP

        container_name = path_tokens[1]

        self.storage_handle.create_container(container_name)

        return 0

    def rmdir(self, path):
        logging.debug("rmdir(path='%s')" % (path,))

        path_tokens = path.split('/')

        if 1 == len(path_tokens):
            return -errno.EPERM
        elif 2 == len(path_tokens):
            container_name = path_tokens[1]
   
            try:
                container = self.storage_handle.get_container(container_name)
            except ContainerDoesNotExistError:
                return -errno.ENOENT

            if 0 != len(container.list_objects()):
                return -errno.ENOTEMPTY

            container.delete()

            return 0
        elif 3 <= len(path_tokens):
            return -errno.EOPNOTSUPP

    def open(self, path, flags):
        logging.debug("open(path='%s', flags='%s')" % (path, flags))
        path_tokens = path.split('/')

        if 3 != len(path_tokens):
            return -errno.EOPNOTSUPP

        container_name, object_name = path_tokens[1], path_tokens[2]
        try:
            container = self.storage_handle.get_container(container_name)
            obj = container.get_object(object_name)
        except ContainerDoesNotExistError, ObjectDoesNotExistError:
            return -errno.ENOENT

        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        logging.debug("read(path='%s', size=%s, offset=%s)" % (path, size, offset))

        path_tokens = path.split('/')
        if 3 != len(path_tokens):
            return -errno.EOPNOTSUPP

        container_name, object_name = path_tokens[1], path_tokens[2]
        try:
            container = self.storage_handle.get_container(container_name)
            obj = container.get_object(object_name)
        except ContainerDoesNotExistError, ObjectDoesNotExistError:
            return -errno.ENOENT

        try:
            content = ''.join([line for line in obj.as_stream()])
        except:
            logging.exception("error reading file content")
            return

        slen = len(content)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            response = content[offset:offset+size]
        else:
            response = ''
        return response

def main():
    usage="""
cloud storage filesystem

""" + fuse.Fuse.fusage
    server = CloudStorageFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parser.add_option(mountopt='driver', metavar="DRIVER",
                help=("Cloud storage driver to use.\n"
                "Supported values: %s") % ' '.join([attr for attr in dir(Provider)
                        if attr.isupper()]))
    server.parser.add_option(mountopt='access_id', metavar='ACCESS_ID',
            help=("Access id, i.e. account id or name"))
    server.parser.add_option(mountopt='secret', metavar='SECRET',
            help=("Account secret key or password"))
    server.parse(values=server, errex=1)

    if not (hasattr(server, 'driver') and hasattr(server, 'access_id') and \
            hasattr(server, 'secret')):
        print >>sys.stderr, "Please specify driver, access_id and secret."
        sys.exit(1)

    server.main()

if __name__ == '__main__':
    main()
