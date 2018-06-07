#!/usr/bin/env python

# doi registration and update tools

__author__ = 'daisieh'

import re
import os
import subprocess
import sys
import shlex
import tempfile
import urllib
import EZID
import optparse

EZID_CLIENT = None
if 'DOI_SERVER' in os.environ:
    DOI_SERVER = os.environ['DOI_SERVER']
else:
    DOI_SERVER = 'https://ezid.cdlib.org'
if 'DOI_USER' in os.environ:
    DOI_USER = os.environ['DOI_USER']
if 'DOI_PASS' in os.environ:
    DOI_PASSWORD = os.environ['DOI_PASS']



def main():
    is_blackout = False
    
    parser = optparse.OptionParser()
    parser.add_option("--doi", dest="doi", help="doi to register or update")
    parser.add_option("--blackout", dest="is_blackout", action="store_true", help="use blackout transform to save metadata")
    parser.add_option("--action", dest="action", help="register/create/update")
    parser.add_option("--username", dest="username", help="EZID username")
    parser.add_option("--password", dest="password", help="EZID password")
    (options, args) = parser.parse_args()
    opt_array = dict(doi=options.doi, is_blackout=options.is_blackout, action=options.action, username=options.username, password=options.password)
        
    run_ezid(opt_array)
    
def run_ezid(options):
    global EZID_CLIENT, DOI_SERVER, DOI_USER, DOI_PASSWORD
    # options should have doi, is_blackout, action, username, password
    doi = options['doi']
    f = None
    
    if 'pipe' in options:
        fh = options['pipe']
    else:
        fh = sys.stdout
    
    # process username/password
    if options['username'] is None or options['password'] is None:
        if DOI_USER is None and DOI_PASSWORD is None:
            sys.exit("Username and password must be provided")
    else:
        DOI_USER = options['username']
        DOI_PASSWORD = options['password']

    if EZID_CLIENT is None:
        EZID_CLIENT = EZID.EZIDClient(server=DOI_SERVER, credentials={'username':DOI_USER, 'password':DOI_PASSWORD})
        try:
            s = subprocess.check_output(['which', 'xsltproc'])
        except subprocess.CalledProcessError as e:
            sys.exit("xsltproc is not installed. Please install using apt-get install xsltproc or similar.")
    
    # add action
    if (options['action'] == 'register') or (options['action'] == 'create'): 
        action = "create"
    elif (options['action'] == 'update'):
        action = "update"
    else:
        fh.write("%s is not a valid action\n" % (options['action']))
        return
    
    # add ezid doi to register
    doi_matcher = re.match("(doi:)*(10.\d+\/)(.+)", doi)
    if doi_matcher is not None:
        dc_doi = "doi:%s%s" % (doi_matcher.group(2), doi_matcher.group(3).upper())
        raw_doi = "doi:%s%s" % (doi_matcher.group(2), doi_matcher.group(3).lower())
    else:
        fh.write("No properly formatted DOI provided\n")
        return
    
    # add target:
    if 'DRYAD_URL' in os.environ:
        DRYAD_URL = os.environ['DRYAD_URL']
    else:
        DRYAD_URL = 'https://datadryad.org'
        
    target_url = '%s/resource/%s' % (DRYAD_URL, raw_doi)
    
    mets_file = tempfile.NamedTemporaryFile(delete=False)
    urllib.urlretrieve('%s/mets.xml' % (target_url), mets_file.name)
    crosswalk_file = tempfile.NamedTemporaryFile(delete=False)
    if options['is_blackout'] is True:
        urllib.urlretrieve('https://raw.githubusercontent.com/datadryad/dryad-repo/dryad-master/dspace/config/crosswalks/DIM2DATACITE-BLACKOUT.xsl', crosswalk_file.name)
        target_url = DRYAD_URL + '/publicationBlackout'
    else:   
        urllib.urlretrieve('https://raw.githubusercontent.com/datadryad/dryad-repo/dryad-master/dspace/config/crosswalks/DIM2DATACITE.xsl', crosswalk_file.name)
    cmd = 'xsltproc %s %s' % (crosswalk_file.name, mets_file.name)
    (metadata, stderrdata) = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    data['_target'] = target_url
    
    # add datacite data
    data['datacite'] = metadata.decode('utf-8')
    
    if action == "create":
        print EZID_CLIENT.create(dc_doi, data)
    elif action == "update":
        print EZID_CLIENT.update(dc_doi, data)
    
#     ['create', 'doi:10.5061/DRYAD.8157N', '_target', 'http://datadryad.org/resource/doi:10.5061/dryad.8157n', 'datacite', '@/Users/daisie/Desktop/test.xml']
    process(args, fh)
    os.remove(f.name)
    os.remove(crosswalk_file.name)
    os.remove(mets_file.name)

if __name__ == '__main__':
    main()

