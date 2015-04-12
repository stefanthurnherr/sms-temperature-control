#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
#import threading
#from multiprocessing import Process, Lock


def try_acquire_lock(lock_file_path):
    #print("Trying to acquire lock {0}...".format(lock_file_path))

    # python 3.3 introduced the 'x' flag for open() which fails if file exists
    # but we're still on python 2.7 ...
    # another possible solution would be fcntl.lockf()

    if os.path.exists(lock_file_path):
        return False

    with open(lock_file_path, 'w') as f:
        f.write(str(os.getpid()))
        return True


def try_release_lock(lock_file_path):
    #print("Releasing lock {0}".format(lock_file_path))
    try:
        os.remove(lock_file_path)
        return True
    except OSError as e:
        print("Ignoring error (myPID:{0}) that occurred when trying to remove lock file '{1}': {2}".format(os.getpid(), lock_file_path, e))
        return not os.path.exists(lock_file_path) # not thread-safe, but good enough since script runs one per minute


