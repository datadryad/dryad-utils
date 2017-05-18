#!/usr/bin/env python

# fix authority values for authors to new format for orcids: "orcid:xxxxxxxx"

__author__ = 'daisieh'

import re
import os
import sys
import string
from sql_utils import rows_from_query

def update_authority(authority, metadata_value_id):
    new_authority = string.replace(authority, "will be generated::orcid::", "orcid:")
    sql = "update metadatavalue set authority = \'%s\' where metadata_value_id = %s" % (new_authority, metadata_value_id)
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    print cmd
    return os.popen(cmd)
        

def main():
    bad_authorities = rows_from_query("select metadata_value_id, authority from metadatavalue where metadata_field_id = 3 and authority like 'will%'")
    print len(bad_authorities)
    for entry in bad_authorities:
        update_authority(entry[1],entry[0])

if __name__ == '__main__':
    main()

