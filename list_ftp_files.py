#!/usr/bin/env python

__author__ = 'daisie'

import os
import re

TRANSFER_PATH = '/opt/dryad-data/largeFilesToDeposit/transfer-complete/'

def main():
    for dirname, dirnames, filenames in os.walk(TRANSFER_PATH):
        # print path to all filenames.
        for filename in filenames:
            relpath = os.path.relpath(dirname,TRANSFER_PATH)
            print os.path.join(relpath, filename)


if __name__ == '__main__':
    main()

