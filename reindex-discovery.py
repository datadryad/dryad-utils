#!/usr/bin/env python

# Reindex items that were archived during a particular date range. Queries the database for those items and then runs update-discovery-index on them.

__author__ = 'daisieh'

import re
import os
import sys
import tempfile
from optparse import OptionParser
from datetime import datetime, date, time
from doi_tool import run_ezid
from sql_utils import dict_from_query, rows_from_query, get_field_id

# Global variables that are initialized farther down.
_username = None
_password = None
    
def reindex_item(item_id):
    cmd = "/opt/dryad/bin/dspace update-discovery-index -i %s" % str(item_id)
    (result1, result2) = os.popen4(cmd)
    m = re.search('Wrote Item: (.*) to Index', result2.read())
    if m is not None:
        return m.group(1) + "\n"
    
def verify_archived_item(item_id):
    doi_field_id = get_field_id('dc.date.accessioned')
    doi = dict_from_query("select text_value from metadatavalue where item_id = %s and metadata_field_id = %s;" % (item_id, doi_field_id))['text_value']
    if doi is None:
        return False
    return True

def update_ezid(item_id, f):
    global _username, _password
    doi_field_id = get_field_id('dc.identifier')
    doi = dict_from_query("select text_value from metadatavalue where item_id = %s and metadata_field_id = %s;" % (item_id, doi_field_id))['text_value']
    if doi is not None:
        options = dict(doi=doi, is_blackout='False', action='update', username=_username, password=_password, pipe=f)
        run_ezid(options)

def main():
    parser = OptionParser()
    parser.add_option("--date_from", dest="date_from", help="find items archived after this date")
    parser.add_option("--date_to", dest="date_to", help="find items archived before this date")
    parser.add_option("--item_from", dest="item_from", help="starting item_id for process")
    parser.add_option("--item_to", dest="item_to", help="ending item_id for process")
    parser.add_option("--username", dest="username", help="EZID username")
    parser.add_option("--password", dest="password", help="EZID password")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True)
    parser.add_option("--log", dest="log_file", help="optional log file")
    (options, args) = parser.parse_args()
    global _username, _password
    _username = options.username
    _password = options.password
    
    if options.log_file is not None:
        f = open(options.log_file, 'w')
    else: 
        if options.verbose is True:
            f.sys.stdout
        else:
            f = tempfile.NamedTemporaryFile()
            print f.name
    
    sql = "select item_id from item where owning_collection = 2 and in_archive = 't' order by item_id asc"    
    if options.date_from is not None or options.date_to is not None:
        if options.date_from is None:
            startdate = datetime.strptime("1900-01-01", "%Y-%m-%d")
        else:
            startdate = datetime.strptime(options.date_from, "%Y-%m-%d")
        if options.date_to is None:
            enddate = date.today()
        else:
            enddate = datetime.strptime(options.date_to, "%Y-%m-%d")        
        sql = "select * from item where owning_collection = 2 and item.in_archive = 't' and item.last_modified >= '%s' and item.last_modified <= '%s'" % (startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
    elif options.item_from is not None or options.item_to is not None:
        if options.item_from is None:
            start = 0
        else:
            start = options.item_from
        if options.item_to is None:
            end = dict_from_query("select last_value from item_seq")['last_value']
        else:
            end = options.item_to
        f.write("%s to %s\n" % (str(start), str(end)))
        sql = "select item_id from item where owning_collection = 2 and in_archive = 't' and item_id >= %s and item_id <= %s order by item_id asc" % (str(start), str(end))
    items = rows_from_query (sql)
    labels = dict(zip(items[0], range(0,len(items[0]))))
    f.write("%d items to index\n" % (len(items) -2))
    f.flush()
    curr_item = ""
    index = 1
    last_index = len(items) -2
    for item in items[1:-1]:
        item_id = item[labels['item_id']]
        if item_id == curr_item:
            continue
        curr_item = item_id
        f.write("%d of %d: indexing %s:\n" % (index, last_index, item_id))
        index = index + 1
        if not verify_archived_item(item_id):
            sys.stderr.write("ERROR: archived item %s does not have a dc.date.accessioned" % (item_id))
            f.write("ERROR: archived item %s does not have a dc.date.accessioned" % (item_id))
            sys.stderr.flush()
        else:
            f.write(reindex_item(item_id))
            update_ezid(item_id, f)
            f.flush()
    f.write("DONE\n")
    f.close()
if __name__ == '__main__':
    main()

