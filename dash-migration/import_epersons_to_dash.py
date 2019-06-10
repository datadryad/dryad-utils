#!/usr/bin/env python

import optparse
import re
import os
import datetime


# Use bash dryad-utils/aws-tools/psql_query.sh 'select eperson_id, email, firstname, lastname from eperson'
# to get a file of all epersons

global HOST, DB, USER, PASSWORD
HOST, DB, USER, PASSWORD = None, None, None, None

def sql_query(sql):
    global HOST, DB, USER, PASSWORD
    hostflag, dbflag, userflag, passflag = "", "", "", ""
    if HOST is not None:
        hostflag = ' -h' + HOST
    if DB is not None:
        dbflag = ' -D' + DB
    if USER is not None:
        userflag = ' -u' + USER
    if PASSWORD is not None:
        passflag = ' -p' + PASSWORD
    result = os.popen("mysql%s%s%s%s -e \"%s\"" % (hostflag, dbflag, userflag, passflag, sql))
    return result

def dict_from_query(sql):
    result = sql_query(sql)
    if result is None:
        return None
    output = [line.strip().split('\t') for line in result.readlines()]
    if len(output) < 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        result = dict(zip(output[0],output[1]))
        return result

def main():
    global HOST, DB, USER, PASSWORD

    parser = optparse.OptionParser()
    parser.add_option("--epersons", dest="eperson_file", help="tab-delimited eperson file")
    parser.add_option("--host", dest="host", help="MySQL server address")
    parser.add_option("--db", dest="database", help="MySQL database")
    parser.add_option("--user", dest="username", help="MySQL username")
    parser.add_option("--password", dest="password", help="MySQL password")
    (options, args) = parser.parse_args()

    if options.host is not None:
        HOST = options.host
    if options.database is not None:
        DB = options.database
    if options.username is not None:
        USER = options.username
    if options.password is not None:
        PASSWORD = options.password
            
    with open(options.eperson_file) as f:
        epersons = f.read().splitlines()
    
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    
    for eperson in epersons:
        eperson_parts = eperson.split("\t")
        print eperson_parts[1]
        eperson_dict = dict_from_query('select * from stash_engine_users where email = \'%s\'' % eperson_parts[1])
        if eperson_dict is not None and eperson_dict['email'] == eperson_parts[1]:
            result = sql_query('update stash_engine_users set eperson_id = \'%s\' where email = \'%s\'' % (eperson_parts[0], eperson_parts[1]))
        else:
            result = sql_query('insert into stash_engine_users (first_name, last_name, email, created_at, updated_at, tenant_id, role, eperson_id) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'dryad\', \'user\', \'%s\')' % (eperson_parts[2], eperson_parts[3], eperson_parts[1], timestamp, timestamp, eperson_parts[0]))
        if result.close() is None:
            print "\tSUCCESS"
        else:
            print "\tERROR"


if __name__ == '__main__':
    main()

