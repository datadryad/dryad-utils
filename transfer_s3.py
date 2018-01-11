#!/usr/bin/env python

__author__ = 'daisie'

import os
import re
import json
import hashlib

## Make sure you've set the FTP_BUCKET environment variable.

TRANSFER_PATH = '/dryad-data/transfer-complete/'
FTP_BUCKET = os.environ['FTP_BUCKET']

def main():
    cmd = 'aws s3 ls s3://%s/ --recursive' % (FTP_BUCKET)
    results = list(os.popen(cmd))
    for file in results:
        parts = re.split('\s+', file, 3)
        if (re.match("^\.", parts[3]) is None):
            key = parts[3].rstrip()
            print key
            cmd = 'aws s3api head-object --bucket %s --key "%s"' % (FTP_BUCKET, key)
            metadata = json.load(os.popen(cmd))
            if ('md5' not in metadata['Metadata']):
                print "  ...calculating and adding an md5 tag"
                hash = hashlib.md5()
                with open(TRANSFER_PATH + key) as f:
                    for chunk in iter(lambda: f.read(4096), ""):
                        hash.update(chunk)
                md5 = hash.hexdigest()
                cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (FTP_BUCKET, key, FTP_BUCKET, key, md5)
                os.popen(cmd)
                print "  md5 tag of %s was added" % (md5)
            else:
                print "  md5 tag is %s" % (metadata['Metadata']['md5'])

if __name__ == '__main__':
    main()

