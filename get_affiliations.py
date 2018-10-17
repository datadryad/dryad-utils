#!/usr/bin/env python

# Report affiliations for authors of packages in Dryad using Crossref API
# Either run with --list to get a fresh list of all possible DOIs
# or with --report [funder/affiliation/publisher] --doi [doi]

__author__ = 'daisieh'

import re
import os
import sys
import requests
import json
import optparse
from sql_utils import rows_from_query, get_field_id, var_from_query

def main():
    parser = optparse.OptionParser()
    parser.add_option("--doi", dest="doi", help="doi to get crossref report for")
    parser.add_option("--list", dest="list_mode", action="store_true", help="list all available dois")
    parser.add_option("--report", dest="report", help="funder/affiliation/publisher")
    (options, args) = parser.parse_args()
    
    pub_doi_field = get_field_id('dc.relation.isreferencedby')
    if options.list_mode:
        sql = 'select mdv.text_value, item.item_id from metadatavalue as mdv, item where item.item_id = mdv.item_id and mdv.metadata_field_id = %s and item.owning_collection = 2 order by item.item_id desc' % (pub_doi_field)
        pub_doi_list = rows_from_query(sql)
        pub_doi_list.pop(0)
        pub_doi_list.pop()
        for pub_doi_item in pub_doi_list:
            print pub_doi_item[0]
    else:
        if options.doi is None or options.report is None:
            print "Either use `--list` or `--report [funder/affiliation/publisher] --doi [doi]`"
            exit
        sql = "select mdv.text_value, item.item_id from metadatavalue as mdv, item where item.item_id = mdv.item_id and mdv.metadata_field_id = %s and item.owning_collection = 2 and mdv.text_value='%s'" % (pub_doi_field, options.doi)
        pub_doi_list = rows_from_query(sql)
        pub_doi_list.pop(0)
        pub_doi_list.pop()
        if pub_doi_list is not None:
            process_pub_doi(pub_doi_list[0], options.report)

def process_pub_doi(pub_doi_item, report_type):
    dryad_doi_field = get_field_id('dc.identifier')
    title_field = get_field_id('dc.title')
    pub_name_field = get_field_id('prism.publicationName')
    m = re.search('^doi:(.+)', pub_doi_item[0])
    if m is not None:
        pub_doi = m.group(0)
        item_id = pub_doi_item[1]
        dryad_doi = var_from_query('select text_value from metadatavalue where item_id = %s and metadata_field_id = %s' % (item_id, dryad_doi_field), 'text_value')
        title = var_from_query('select text_value from metadatavalue where item_id = %s and metadata_field_id = %s' % (item_id, title_field), 'text_value')
        pub_name = var_from_query('select text_value from metadatavalue where item_id = %s and metadata_field_id = %s' % (item_id, pub_name_field), 'text_value')
        try:
            r = requests.get('https://api.crossref.org/works/%s?mailto=admin@datadryad.org' % pub_doi)
            if r.status_code == 200:
                if report_type == 'affiliation':
                    authors = find_authors(r.json())
                    for author in authors:
                        author = author.replace('\n', ' ')
                        print '%s\t%s\t%s\t%s\t%s\t%s' % (item_id, dryad_doi, title, pub_doi, pub_name, author.encode('utf-8'))
                elif report_type == 'funder':
                    funders = find_funders(r.json())
                    for funder in funders:
                        funder = funder.replace('\n', ' ')
                        print '%s\t%s\t%s\t%s\t%s\t\t\t\t%s' % (item_id, dryad_doi, title, pub_doi, pub_name, funder.encode('utf-8'))
                elif report_type == 'publisher':
                    publisher = find_publisher(r.json()).replace('\n', ' ')
                    print '%s\t%s\t%s\t%s\t%s\t\t\t\t%s' % (item_id, dryad_doi, title, pub_doi, pub_name, publisher.encode('utf-8'))
            else:
                print "%s\tno result for %s: %s" % (item_id, pub_doi, r.status_code)
        except:
            print "error occurred while executing " + pub_doi
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

def find_publisher(pub_json):
    if 'message' in pub_json:
        if 'publisher' in pub_json['message']:
            return pub_json['message']['publisher']


if __name__ == '__main__':
    main()

