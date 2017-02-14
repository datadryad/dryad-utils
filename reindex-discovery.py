#!/usr/bin/env python

# Reindex items that were archived during a particular date range. Queries the database for those items and then runs update-discovery-index on them.

__author__ = 'daisieh'

import re
import os
from optparse import OptionParser
from datetime import datetime, date, time

# Global variables that are initialized farther down.

def dict_from_query(sql):
    # Now execute it
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        return dict(zip(output[0],output[1]))

def rows_from_query(sql):
    # Now execute it
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        return output

def get_field_id(name):
    parts = re.split('\.', name)
    schema = dict_from_query("select metadata_schema_id from metadataschemaregistry where short_id = '%s'" % parts[0])['metadata_schema_id']
    if len(parts) > 2:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier = '%s'" % (schema, parts[1], parts[2]))['metadata_field_id']
    else:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier is null" % (schema, parts[1]))['metadata_field_id']
    return field_id
    
def reindex_item(item_id):
    cmd = "/opt/dryad/bin/dspace update-discovery-index -i %s" % str(item_id)
    (result1, result2) = os.popen4(cmd)
    m = re.search('Wrote Item: (.*) to Index', result2.read())
    if m is not None:
        print m.group(1)
    
    
def main():
    parser = OptionParser()
    parser.add_option("--date_from", dest="date_from", help="find items archived after this date")
    parser.add_option("--date_to", dest="date_to", help="find items archived before this date")
    parser.add_option("--cursor", dest="cursor", help="starting item_id for process")
    (options, args) = parser.parse_args()
    
    startdate = datetime.strptime(options.date_from, "%Y-%m-%d")
    enddate = datetime.strptime(options.date_to, "%Y-%m-%d")
    acc_field = get_field_id('dc.date.accessioned')
    sql = "select item.item_id as item_id, mdv.text_value as date from item, metadatavalue as mdv where item.item_id = mdv.item_id and item.owning_collection = 2 and mdv.metadata_field_id = %s and item.in_archive = 't' and mdv.text_value >= '%s' and mdv.text_value <= '%s'" % (acc_field, startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
    items = rows_from_query (sql)
    curr_item = ""
    labels = dict(zip(items[0], range(0,len(items[0]))))
    for item in items[1:-1]:
        item_id = item[labels['item_id']]
        item_doi = item[labels['date']]
        if item_id == curr_item:
            continue
        curr_item = item_id
        print "%s\t%s" % (item_id, item_doi)
        reindex_item(item_id)
if __name__ == '__main__':
    main()

