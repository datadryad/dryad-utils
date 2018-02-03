#!/usr/bin/env python

# Create a database at AWS (or locally, if that is the argument given for db_host)
# If specified RDS already exists at AWS, dumps the database and imports a fresh copy.

__author__ = 'daisie'

import os
import re
import sys
import json
import time

PGPASSWORD = os.environ['PGPASSWORD']
FULL_DRYAD_DB_HOST = os.environ['DRYAD_DB_HOST']
DRYAD_DB_HOST = FULL_DRYAD_DB_HOST.split('.')[0]
HOST_SUFFIX = '.co33oyzjqasf.us-east-1.rds.amazonaws.com' # this is always the same for Dryad at us-east-1

def db_status(db_name):
    result = os.popen('aws rds describe-db-instances --db-instance-identifier %s' % (db_name)).read()
    if (result != ""):
        metadata = json.loads(result)
        if len(metadata['DBInstances']) > 0:
            return metadata['DBInstances'][0]['DBInstanceStatus']
    return "n/a"
        
# if (metadata['DBInstances'])


def main():
    if len(sys.argv) == 1:
        print "usage `python rebuild_db.py <db dump file> <db host>[optional: uses $DRYAD_DB_HOST as default]`"
        exit(0)
        
    if len(sys.argv) > 1:
        db_source = sys.argv[1]
    
    if len(sys.argv) > 2:
        db_host = sys.argv[2]
    else:
        db_host = DRYAD_DB_HOST

    if (db_status(db_host) == "n/a"):
        print 'create a new RDS'
        cmd = 'aws rds create-db-instance --db-name dryad_repo --db-instance-identifier %s --allocated-storage 10 --db-instance-class db.t2.small --engine postgres --master-username dryad_app --master-user-password %s --vpc-security-group-ids "sg-77d83c0b" --backup-retention-period 0' % (db_host, PGPASSWORD)
        os.popen(cmd)
        time.sleep(10)

    while True:
        status = db_status(db_host)
        print 'status is "%s"...' % (status)
        if status == "available":
            break
        time.sleep(20)
            
    cmd = 'import_pg_dump.sh %s %s' % (db_source, db_host+HOST_SUFFIX)
    os.popen(cmd)
        
    print "done"


if __name__ == '__main__':
    main()

