#!/usr/bin/env python

# doi registration and update tools

__author__ = 'daisieh'

import re
import os
import subprocess
import sys
import shlex
import tempfile
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
    
    doi = options.doi
    f = None
    args = []
    
    # process username/password
    if options.username is None or options.password is None:
        print "Username and password must be provided"
        return
    args.append("%s:%s" % (options.username, options.password))
    
    # add action
    if (options.action == 'register') or (options.action == 'create'): 
        args.append("create")
    elif (options.action == 'update'):
        args.append("update")
    else:
        print "%s is not a valid action" % (options.action)
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
    
    if options.is_blackout is True:
        cmd = 'xsltproc /opt/dryad/config/crosswalks/DIM2DATACITE-BLACKOUT.xsl %s' % doi_path
        target_url = 'http://datadryad.org/publicationBlackout'
    else:   
        cmd = 'xsltproc /opt/dryad/config/crosswalks/DIM2DATACITE.xsl %s' % doi_path
    f = tempfile.NamedTemporaryFile(delete=False)
    subprocess.Popen(shlex.split(cmd), stdout=f).communicate()

    args.append(target_url)
    
    # add datacite file
    args.append('datacite')
    args.append('@%s' % f.name)
    
#     ['create', 'doi:10.5061/DRYAD.8157N', '_target', 'http://datadryad.org/resource/doi:10.5061/dryad.8157n', 'datacite', '@/Users/daisie/Desktop/test.xml']
    process(args)
    os.remove(f.name)

if __name__ == '__main__':
    main()

