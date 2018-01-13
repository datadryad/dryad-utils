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
    if len(sys.argv) < 2:
        print "Bucket is required as an argument"
        exit(0)
    bucket = sys.argv[1]
    
    # collect all the keys from the bucket:
    next_token = " "
    keys = []
    
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
    for key in keys:
        if (re.match("^\.", key) is None):
            print key
            cmd = 'aws s3api head-object --bucket %s --key "%s"' % (bucket, key)
            metadata = json.load(os.popen(cmd))
            if ('md5' not in metadata['Metadata']):
                md5 = metadata['ETag']
                if "-" in md5:
                    print "  ETag is not an md5"
                else:
                    cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (bucket, key, bucket, key, md5)
                    os.popen(cmd)
                    print "  added md5 tag of %s" % (md5)
            else:
                print "  md5 tag is %s" % (metadata['Metadata']['md5'])
        sys.stdout.flush()            

if __name__ == '__main__':
    main()

