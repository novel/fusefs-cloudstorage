fusefs-cloudstorage
-------------------
fusefs-cloudstorage is a FUSE-based filesystem providing
access to various cloud storages like Rackspace CloudFiles
and Amazon S3.

It is based on libcloud storage interface that appeared in
libcloud 0.5.

Requirements
------------
* fuse-python http://sourceforge.net/projects/fuse/files/fuse-python/0.2.1/
* libcloud >= 0.5.0 (http://libcloud.apache.org/)

Usage
-----

    ./lc-fuse.py -f -o driver=CLOUDFILES_US -o access_id=$your_loging \
     -o secret=$your_pass mountpoint

* Author: Roman Bogorodskiy <bogorodskiy@gmail.com>
* Github: https://github.com/novel/fusefs-cloudstorage
