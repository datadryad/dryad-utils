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
from optparse import OptionParser

from ezid import process

def main():
    is_blackout = False
    
    parser = OptionParser()
    parser.add_option("--doi", dest="doi", help="doi to register or update")
    parser.add_option("--blackout", dest="is_blackout", action="store_true", help="use blackout transform to save metadata")
    parser.add_option("--action", dest="action", help="register/create/update")
    parser.add_option("--username", dest="username", help="EZID username")
    parser.add_option("--password", dest="password", help="EZID password")
    (options, args) = parser.parse_args()
    opt_array = dict(doi=options.doi, is_blackout=options.is_blackout, action=options.action, username=options.username, password=options.password)
    run_ezid(opt_array)
    
def run_ezid(options):
    # options should have doi, is_blackout, action, username, password
    doi = options['doi']
    f = None
    args = []
    
    # process username/password
    if options['username'] is None or options['password'] is None:
        print "Username and password must be provided"
        return
    args.append("%s:%s" % (options['username'], options['password']))
    
    # add action
    if (options['action'] == 'register') or (options['action'] == 'create'): 
        args.append("create")
    elif (options['action'] == 'update'):
        args.append("update")
    else:
        print "%s is not a valid action" % (options['action'])
        return
    
    # add ezid doi to register
    doi_matcher = re.match("(doi:)*(.+)\/(.+)", doi)
    if doi_matcher is not None:
        args.append("doi:%s/%s" % (doi_matcher.group(2), doi_matcher.group(3).upper()))
    else:
        print "No properly formatted DOI provided"
        return
    
    # add target:
    args.append('_target')
    doi_path = 'http://datadryad.org/resource/%s/mets.xml' % (doi)
    target_url = 'http://datadryad.org/resource/%s' % (doi)
    
    crosswalk_file = tempfile.NamedTemporaryFile(delete=False)
    if options['is_blackout'] is True:
        urllib.urlretrieve('https://raw.githubusercontent.com/datadryad/dryad-repo/dryad-master/dspace/config/crosswalks/DIM2DATACITE-BLACKOUT.xsl', crosswalk_file.name)
        cmd = 'xsltproc %s %s' % (crosswalk_file.name, mets_file.name)
        target_url = 'http://datadryad.org/publicationBlackout'
    else:   
        urllib.urlretrieve('https://raw.githubusercontent.com/datadryad/dryad-repo/dryad-master/dspace/config/crosswalks/DIM2DATACITE.xsl', crosswalk_file.name)
        cmd = 'xsltproc %s %s' % (crosswalk_file.name, mets_file.name)
    f = tempfile.NamedTemporaryFile(delete=False)
    subprocess.Popen(shlex.split(cmd), stdout=f).communicate()

    args.append(target_url)
    
    # add datacite file
    args.append('datacite')
    args.append('@%s' % f.name)
    
#     ['create', 'doi:10.5061/DRYAD.8157N', '_target', 'http://datadryad.org/resource/doi:10.5061/dryad.8157n', 'datacite', '@/Users/daisie/Desktop/test.xml']
    process(args)
    os.remove(f.name)
    os.remove(crosswalk_file.name)

if __name__ == '__main__':
    main()

