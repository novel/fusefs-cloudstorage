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

    ./cloudstorage.py -f -o driver=CLOUDFILES_US -o access_id=$your_login \
     -o secret=$your_pass mountpoint

Here:

 * CLOUDFILES\_US is a name of the driver. Plase use `cloudstorage.py -h` to get
   list of available drivers.
 * $your\_login and $your\_pass mean your login (access id, etc)  and password (secret)
   to your account

* Author: Roman Bogorodskiy <bogorodskiy@gmail.com>
* Github: https://github.com/novel/fusefs-cloudstorage
