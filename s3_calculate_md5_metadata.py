#!/usr/bin/env python

# Add md5 as a metadata tag on S3 objects in a bucket. If the ETag is not an md5 (contains a hyphen), 
# flag the item to deal with later.

__author__ = 'daisie'

import os
import re
import sys
import json
import hashlib

def main():
    if len(sys.argv) < 3:
        print "bucket and key are required as an argument"
        exit(0)
    bucket = sys.argv[1]
    key = sys.argv[2]
    
    if (re.match("^\.", key) is None):
        cmd = 'aws s3api head-object --bucket %s --key "%s"' % (bucket, key)
        metadata = json.load(os.popen(cmd))
        if ('md5' not in metadata['Metadata']):
            md5 = metadata['ETag']
            if "-" in md5:
                print "  ETag is not an md5"
                local_path = '/opt/dryad-data/temp/%s' % (key)
                cmd = 'aws s3 cp "s3://%s/%s" "%s"' % (bucket, key, local_path)
                os.popen(cmd)
                print "  ...calculating and adding an md5 tag"
                hash = hashlib.md5()
                with open(local_path) as f:
                    for chunk in iter(lambda: f.read(4096), ""):
                        hash.update(chunk)
                md5 = hash.hexdigest()
                os.remove(local_path)
                cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (bucket, key, bucket, key, md5)
                os.popen(cmd)
                print "  added md5 tag of %s" % (md5)
            else:
                cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (bucket, key, bucket, key, md5)
                os.popen(cmd)
        else:
            print "  md5 tag is %s" % (metadata['Metadata']['md5'])
    sys.stdout.flush()            

if __name__ == '__main__':
    main()

