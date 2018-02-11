#!/usr/bin/env python

# Copy all items from one bucket to another, adding md5 tags as necessary. 
# If md5 is not present, calculate from ETag, but if ETag is not md5, flag for later.

__author__ = 'daisie'

import os
import re
import sys
import json
import hashlib

def main():
    if len(sys.argv) < 3:
        print "Source and target buckets are required as arguments"
        exit(0)
    bucket = sys.argv[1]
    target_bucket = sys.argv[2]
    
    keys = []

    if len(sys.argv) == 4:
        keys_file = sys.argv[3]
        with open(keys_file) as f:
            keys = f.read().splitlines()
    else:
        # collect all the keys from the bucket:
        next_token = " "

        while next_token is not "":
            base_cmd = 'aws s3api list-objects-v2 --bucket %s --page-size 1000 --max-items 1000 %s' % (bucket, next_token)
            results = json.load(os.popen(base_cmd))
            if results is None:
                print "empty bucket"
                exit(1)

            if 'NextToken' in results:
                next_token = '--starting-token ' + results['NextToken']
            else:
                next_token = ""

            for object in results['Contents']:
                keys.append(object['Key'])

    print "added %s keys" % (len(keys))
    sys.stdout.flush()
    
    # now that we have all the keys, check their md5 tags:
    count = 0
    for key in keys:
        count = count + 1
        cmd = 'aws s3api head-object --bucket %s --key "%s"' % (target_bucket, key)
        if (os.popen(cmd).read() != ""):
            print "%s: %s already exists in target" % (count, key)
            sys.stdout.flush()
            continue
        
        if (re.match("^\.", key) is None):
            print '%s: %s' % (count, key)
            cmd = 'aws s3api head-object --bucket %s --key "%s"' % (bucket, key)
            metadata = json.load(os.popen(cmd))
            if ('md5' not in metadata['Metadata']):
                md5 = metadata['ETag']
                if "-" in md5:
                    print "  ETag is not an md5"
                else:
                    print "  added md5 tag of %s" % (md5)
            else:
                md5 = metadata['Metadata']['md5']
                print "  md5 tag is %s" % (md5)
            cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (bucket, key, target_bucket, key, md5)
            os.popen(cmd)
        sys.stdout.flush()            

if __name__ == '__main__':
    main()

