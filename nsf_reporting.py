#!/usr/bin/env python

# Creates a report of NSF-sponsored packages archived during a date range.

__author__ = 'daisieh'

import re
import os
import sys
import shutil
import hashlib
from time import strptime, strftime
# import datetime

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

def update_sponsor_id(name, item_id):
    sql = "update shoppingcart set sponsor_id = %s where journal='%s'" % (item_id, name)
    cmd = "psql -U dryad_app dryad_repo -c \"%s\"" % sql
    print os.popen(cmd).read()

def get_field_id(name):
    parts = re.split('\.', name)
    schema = dict_from_query("select metadata_schema_id from metadataschemaregistry where short_id = '%s'" % parts[0])['metadata_schema_id']
    if len(parts) > 2:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier = '%s'" % (schema, parts[1], parts[2]))['metadata_field_id']
    else:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier is null" % (schema, parts[1]))['metadata_field_id']
    return field_id

def main():
    if len(sys.argv) < 3:
        print "Start and end dates must be specified"
        return
            
    startdate = strptime(sys.argv[1], "%Y-%m-%d")
    enddate = strptime(sys.argv[2], "%Y-%m-%d")
    prov_field = get_field_id('dc.description.provenance')
    items = rows_from_query ("select distinct nsf.item_id, substring(prov.text_value, 'Made available in DSpace on (\d+-\d+-\d+)T.+') from metadatavalue as nsf, metadatavalue as prov where nsf.authority='NSF' and nsf.item_id=prov.item_id and prov.metadata_field_id=%s and prov.text_value like 'Made available in DSpace%%' order by substring" % prov_field)
    labels = dict(zip(items[0], range(0,len(items[0]))))
    
    print "item\tarchive date\tdoi\tgrant provided\tis valid?\ttitle\tauthors"
    for item in items[1:-1]:
#     Dryad DOI, grant number provided (with confidence value), article DOI, authors, article title.
        item_id = item[labels['item_id']]
        item_date = strptime(item[labels['substring']], "%Y-%m-%d")
        
        if item_date >= startdate and item_date <= enddate:
            # get the item's DOI:
            doi = dict_from_query("select text_value from metadatavalue where item_id = %s and metadata_field_id = %s" % (item_id, get_field_id('dc.identifier')))['text_value']
            
            # get the item's grant number:
            fundingEntity = dict_from_query("select text_value, authority, confidence from metadatavalue where item_id = %s and metadata_field_id = %s" % (item_id, get_field_id('dryad.fundingEntity'))) 
            grant = fundingEntity['text_value']
            authority = fundingEntity['authority']
            confidence = fundingEntity['confidence']
            if int(confidence) == 600:
                valid = 'True'
            else:
                valid = 'False'
            
                       
            # get the item's authors:
            authors = rows_from_query("select text_value from metadatavalue where item_id = %s and metadata_field_id = %s order by place" % (item_id, get_field_id('dc.contributor.author')))
            authorlist = []
            for author in authors[1:-1]:
                authorlist.append(author[0])
            authorstring = '; '.join(authorlist)
            
            # get the item's title:    
            title = dict_from_query("select text_value from metadatavalue where item_id = %s and metadata_field_id = %s" % (item_id, get_field_id('dc.title')))['text_value'] 
            
            next = '\t'.join([item_id, strftime("%Y-%m-%d", item_date), doi, grant, valid, title, authorstring])
            print '%s' % next
            
if __name__ == '__main__':
    main()

