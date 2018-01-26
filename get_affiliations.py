#!/usr/bin/env python

# Report affiliations for authors of packages in Dryad using Crossref API

__author__ = 'daisieh'

import re
import os
import sys
import requests
import json
from sql_utils import rows_from_query, get_field_id, var_from_query


def main():
    pub_doi_field = get_field_id('dc.relation.isreferencedby')
    if len(sys.argv) > 1:
        sql = "select mdv.text_value, item.item_id from metadatavalue as mdv, item where item.item_id = mdv.item_id and mdv.metadata_field_id = %s and item.owning_collection = 2 and mdv.text_value='%s'" % (pub_doi_field, sys.argv[1])
        pub_doi_list = rows_from_query(sql)
        print pub_doi_list
        for pub_doi_item in pub_doi_list:        
            process_pub_doi(pub_doi_item)
    else:
        sql = 'select mdv.text_value, item.item_id from metadatavalue as mdv, item where item.item_id = mdv.item_id and mdv.metadata_field_id = %s and item.owning_collection = 2' % (pub_doi_field)
        pub_doi_list = rows_from_query(sql)
        print len(pub_doi_list)
        for pub_doi_item in pub_doi_list:
            process_pub_doi(pub_doi_item)


def process_pub_doi(pub_doi_item):
    dryad_doi_field = get_field_id('dc.identifier')
    title_field = get_field_id('dc.title')
    m = re.search('^doi:(.+)', pub_doi_item[0])
    if m is not None:
        pub_doi = m.group(0)
        item_id = pub_doi_item[1]
        dryad_doi = var_from_query('select text_value from metadatavalue where item_id = %s and metadata_field_id = %s' % (item_id, dryad_doi_field), 'text_value')
        title = var_from_query('select text_value from metadatavalue where item_id = %s and metadata_field_id = %s' % (item_id, title_field), 'text_value')
        r = requests.get('http://api.crossref.org/works/%s' % pub_doi)
        if r.status_code == 200:
            authors = find_authors(r.json())
            for author in authors:
                print '%s\t%s\t%s\t%s' % (dryad_doi, title, pub_doi, author.encode('utf-8'))
            funders = find_funders(r.json())
            for funder in funders:
                print '%s\t%s\t%s\t\t\t\t%s' % (dryad_doi, title, pub_doi, funder.encode('utf-8'))
        else:
            print "no result for %s: %s" % (pub_doi, r.status_code)
    sys.stdout.flush()
    
def find_funders(pub_json):
    funder_list = []
    if 'message' in pub_json:
        if 'funder' in pub_json['message']:
            funders = pub_json['message']['funder']
            for funder in funders:
                if 'DOI' in funder:
                    funder_doi = funder['DOI']
                else:
                    funder_doi = ''
                if 'name' in funder:
                    funder_name = funder['name']
                else:
                    funder_name = ''
                if 'award' in funder:
                    funder_awards = ','.join(funder['award'])
                else:
                    funder_awards = ''
                funder_list.append('\t'.join([funder_doi,funder_name,funder_awards]))
    return funder_list

def find_authors(pub_json):
    author_list = []
    if 'message' in pub_json:
        if 'author' in pub_json['message']:
            authors = pub_json['message']['author']
            for author in authors:
                affiliations = author['affiliation']
                if len(affiliations) > 0:
                    for affiliation in affiliations:
                        family = ""
                        given = ""
                        name = ""
                        if 'family' in author:
                            family = author['family']
                        if 'given' in author:
                            given = author['given']
                        if 'name' in affiliation:
                            name = affiliation['name']
                        author_list.append('\t'.join([family, given, name]))
    return author_list

if __name__ == '__main__':
    main()

