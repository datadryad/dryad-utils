#!/usr/bin/env python

import sys
import os
import re
import datetime
import shutil

# Cleans up metadata files in /opt/dryad/submission/JournalMetadata based on the
# canonical manuscript regex to be stored in the concept's
# journal.canonicalManuscriptNumberPattern metadata field.
# 
# Takes two arguments: the journal metadata directory (found in journal.metadataDir 
# in the concept metadata) and the canonical regex (found in 
# journal.canonicalManuscriptNumberPattern in the concept metadata)
#
# Files older than 18 months old are moved into a directory called "obsolete"
# Files not matching the canonical regex are moved into a directory called "extra"
# For all remaining files, a copy is stored in "archived" and only the most recent
# revision is saved in the root directory under the canonical manuscript number.

if len(sys.argv) < 3:
     assert False, 'Usage: cleanup.py [dir] [regex]'

mypath = sys.argv[1]
regex = re.compile(sys.argv[2]+'(.*?)\.xml')


def main():
    found = {}
    notmatch = []
    old = []
    for v in os.listdir(mypath):
         if (file_too_old(os.path.join(mypath,v))) :
            old.append(v)

    if len(old) > 0:
      if 'obsolete' not in os.listdir(mypath):
        os.mkdir(os.path.join(mypath,'obsolete'))
      for fn in old:
        shutil.move(os.path.join(mypath,fn),os.path.join(mypath,'obsolete',fn))

    for fn in os.listdir(mypath):
      if fn == '.git':
        continue
      if fn == 'obsolete':
        continue
      if fn == 'extra':
        continue
      if fn == 'archived':
        continue
      match = regex.match(fn)
      if match:
            if match.group(1) not in found:
                found[match.group(1)] = []         
            found[match.group(1)].append(fn)
      else:
            notmatch.append(fn)
    
    if 'archived' not in os.listdir(mypath):
      os.mkdir(os.path.join(mypath,'archived'))
    if 'extra' not in os.listdir(mypath):
      os.mkdir(os.path.join(mypath,'extra'))
    for fn in notmatch:
      shutil.move(os.path.join(mypath,fn),os.path.join(mypath,'extra',fn))
    for k in found.keys():
      print k
      newestfile = ''
      for v in found[k]:
        print '\t{name}'.format(name=v)
       # move all files to the archive directory
        shutil.move(os.path.join(mypath,v),os.path.join(mypath,'archived',v))
        if (file1_is_newer(v,newestfile)):
            newestfile = v
      print '\tnewest is {name}'.format(name=newestfile) 
        # copy the newest one back with the canonical name
      shutil.copy2(os.path.join(mypath,'archived',newestfile),os.path.join(mypath,k+'.xml'))

def file_too_old(file):
    stat = os.stat(file)
    d = datetime.date.fromtimestamp(stat.st_mtime)
    fromtime = datetime.date.today() - datetime.timedelta(weeks=78)
    if (d < fromtime):
      print '\t\t{name} {date} is too old'.format(name=file,date=d)
      return True
    return False

def file1_is_newer(file1,file2):
    if file1 == '':
        return False
    if file2 == '':
        return True
# first check to see if there is a most-recent revision:
    match = regex.match(file1)
    rev1 = match.group(2)
    match = regex.match(file2)
    rev2 = match.group(2)
    if (rev1 == ''):
        return False
    if (rev1 > rev2):
        return True
     
# then check to see if one is newer
    stat1 = os.stat(os.path.join(mypath,'archived',file1))
    stat2 = os.stat(os.path.join(mypath,'archived',file2))
    if (stat1.st_mtime > stat2.st_mtime):
        return True
    return False

if __name__ == "__main__": main()
