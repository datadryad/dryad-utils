#!/usr/bin/env python

# Re-sync all packages with EZID. Takes two (or three) arguments:
# sync_provenance.py username password start_item
# start_item is the last item_id synced. If not specified, start from 0.

# Parts of the code are liberally taken from http://ezid.cdlib.org/doc/ezid.py

__author__ = 'daisieh'

import re
import os
import sys
import shutil
import hashlib
import codecs
import getpass
import time
import types
import urllib
import urllib2
import tempfile
import subprocess
from sql_utils import dict_from_query, rows_from_query

# Global variables that are initialized farther down.

_server = "https://ezid.cdlib.org"
_username = None
_password = None

MY_DRYAD = "http://daisietest.datadryad.org:9999/resource/"
MY_DRYAD_REPO = "/home/ubuntu/dryad-repo/"

class MyHTTPErrorProcessor (urllib2.HTTPErrorProcessor):
  def http_response (self, request, response):
    # Bizarre that Python leaves this out.
    if response.code == 201:
      return response
    else:
      return urllib2.HTTPErrorProcessor.http_response(self, request, response)
  https_response = http_response

def encode (id):
  return urllib.quote(id, ":/")

def issueRequest (path, data, opener):
    url = "%s/%s" % (_server, path)
    request = urllib2.Request(url)
    request.add_header("Content-Type", "text/plain; charset=UTF-8")
    request.add_data(data.encode("UTF-8"))
    print url
    try:
        connection = opener.open(request)
        response = connection.read()
        return response.decode("UTF-8")
    except urllib2.HTTPError, e:
        sys.stderr.write("%d %s\n" % (e.code, e.msg))
        if e.fp != None:
            response = e.fp.read()
            if not response.endswith("\n"): response += "\n"
            sys.stderr.write(response)
#         sys.exit(1)

def printAnvlResponse (response, sortLines=False):
    response = response.splitlines()
    if sortLines and len(response) >= 1:
        statusLine = response[0]
        response = response[1:]
        response.sort()
        response.insert(0, statusLine)
    for line in response:
        print line

def get_field_id(name):
    parts = re.split('\.', name)
    schema = dict_from_query("select metadata_schema_id from metadataschemaregistry where short_id = '%s'" % parts[0])['metadata_schema_id']
    if len(parts) > 2:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier = '%s'" % (schema, parts[1], parts[2]))['metadata_field_id']
    else:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier is null" % (schema, parts[1]))['metadata_field_id']
    return field_id
    
def is_blackout(item_id):
    prov_field = get_field_id('dc.description.provenance')
    item = dict_from_query("select * from metadatavalue where item_id = %s and metadata_field_id = %s and text_value like '%%Made available in DSpace%%'" % (item_id, prov_field))
    if item is None:
        return True
    return False


def ezid(id, filename, username, password):
    opener = urllib2.build_opener(MyHTTPErrorProcessor())
    h = urllib2.HTTPBasicAuthHandler()
    h.add_password("EZID", _server, username, password)
    opener.add_handler(h)

    # Perform the operation.
    request = []
    f = codecs.open(filename, encoding="UTF-8")
    request += [l.strip("\r\n") for l in f.readlines()]
    f.close()
    data = 'datacite: ' + "".join(request)
#     print data

    response = issueRequest("id/"+encode(id), data, opener)
    if response is not None:
        printAnvlResponse(response)

def main():
    username = sys.argv[1]
    password = sys.argv[2]
    cursor = 0
    if len(sys.argv) > 3:
        cursor = sys.argv[3]
    
    doi_field = get_field_id('dc.identifier')
    items = rows_from_query ("SELECT item.item_id AS item_id, mdv.text_value AS doi FROM item, metadatavalue AS mdv WHERE item.item_id = mdv.item_id AND item.in_archive = 't' AND mdv.metadata_field_id = %s AND mdv.text_value like 'doi%%' and item.item_id > %s order by item.item_id asc" % (doi_field, cursor))
    curr_item = ""
    labels = dict(zip(items[0], range(0,len(items[0]))))
    for item in items[1:-1]:
        item_id = item[labels['item_id']]
        item_doi = item[labels['doi']]
        if item_id == curr_item:
            continue
        curr_item = item_id
        print "%s\t%s" % (item_id, item_doi)
        req = urllib2.Request(MY_DRYAD + item_doi + "/mets.xml")
        res = urllib2.urlopen(req)
        mets = tempfile.NamedTemporaryFile(delete=False)
        mets.write(res.read())
        mets.close()
        output = subprocess.check_output(["xsltproc", MY_DRYAD_REPO + "dspace/config/crosswalks/DIM2DATACITE.xsl", mets.name])
        datacite = tempfile.NamedTemporaryFile(delete=False)
        datacite.write(output)
        datacite.close()
        m = re.search('DOI:(.*)', item_doi.upper())
        item_doi = 'doi:' + m.group(1)
        ezid(item_doi, datacite.name, username, password)
        os.unlink(mets.name)
        os.unlink(datacite.name)
if __name__ == '__main__':
    main()

