#!/usr/bin/env python

# fix errors in database

__author__ = 'daisieh'

import re
import os
import sys
import json
import urllib

def rows_from_query(sql):
    # Now execute it
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        return output[1:-1]

def update_json_row(json_data, manuscript_id):
    sql = "update manuscript set json_data = $$%s$$ where manuscript_id = %s" % (json_data, manuscript_id)
    cmd = "psql -A -U dryad_app dryad_repo -c \'%s\'" % sql
#     print manuscript_id + ": trying to execute command:" 
#     print cmd
    return os.popen(cmd)
        
def update_json(manuscript_id, json_data):
#     test = "manuscript %s has data %s" % (manuscript_id, json_data)
#     print test
#     print "replaced " + str(x) + " occurrences"
    manuscript = json.loads(json_data)
    authors = manuscript["authors"]
    for author in authors[authors.keys()[0]]:
        if "fullName" not in author:
            familyname = author["unicodeFamilyName"]
            givennames = author["unicodeGivenNames"]
            fullname = familyname + ", " + givennames
            if "unicodeFullName" in author:
                del author["unicodeFullName"]
            if "unicodeFamilyName" in author:
                del author["unicodeFamilyName"]
            if "unicodeGivenNames" in author:
                del author["unicodeGivenNames"]
            if "htmlfullName" in author:
                del author["htmlfullName"]
            if "htmlfamilyName" in author:
                del author["htmlfamilyName"]
            if "htmlgivenNames" in author:
                del author["htmlgivenNames"]
            if "normalizedFullName" in author:
                del author["normalizedFullName"]
            if "normalizedFamilyName" in author:
                del author["normalizedFamilyName"]
            if "normalizedGivenNames" in author:
                del author["normalizedGivenNames"]
            author["fullName"] =  fullname
            author["familyName"] =  familyname
            author["givenNames"] =  givennames
        elif "familyName" not in author:
            pat = re.compile("(.*?), (.*)")
            match = pat.match(author["fullName"])
            if match:
                author["familyName"] = match.group(1)
                author["givenNames"] = match.group(2)
        else:
            print "looks okay"
    authors = manuscript["correspondingAuthor"]
    author = authors["author"]
    author["familyName"] =  ""
    author["givenNames"] =  ""
    if "fullName" not in author:
        familyname = author["unicodeFamilyName"]
        givennames = author["unicodeGivenNames"]
        fullname = familyname + ", " + givennames
        if "unicodeFullName" in author:
            del author["unicodeFullName"]
        if "unicodeFamilyName" in author:
            del author["unicodeFamilyName"]
        if "unicodeGivenNames" in author:
            del author["unicodeGivenNames"]
        if "htmlfullName" in author:
            del author["htmlfullName"]
        if "htmlfamilyName" in author:
            del author["htmlfamilyName"]
        if "htmlgivenNames" in author:
            del author["htmlgivenNames"]
        if "normalizedFullName" in author:
            del author["normalizedFullName"]
        if "normalizedFamilyName" in author:
            del author["normalizedFamilyName"]
        if "normalizedGivenNames" in author:
            del author["normalizedGivenNames"]
        author["fullName"] =  fullname
        author["familyName"] =  familyname
        author["givenNames"] =  givennames
    elif "familyName" not in author:
        pat = re.compile("(.*?), (.*)")
        match = pat.match(author["fullName"])
        if match:
            author["familyName"] = match.group(1)
            author["givenNames"] = match.group(2)
    else:
        print "looks okay"
    
    abstract = manuscript["abstract"]
    if abstract is not None:
        abstract = abstract.encode('ascii', 'xmlcharrefreplace')
        pat = re.compile("([\'\"])")
        new_abstract = urllib.quote(abstract)
        new_abstract = re.sub('%20', ' ', new_abstract)
        new_abstract = re.sub('\'', '\'\'', new_abstract)
    
        manuscript["abstract"] = new_abstract

#     return re.sub("\'", "%27", json.dumps(manuscript))
    return json.dumps(manuscript)
    

def main():
    bad_json_rows = rows_from_query("select manuscript_id, json_data, msid from manuscript where json_data NOT LIKE '%familyName%'")
    print len(bad_json_rows)
    for entry in bad_json_rows:
        print "processing " + entry[2]
        good_json = update_json(entry[0], entry[1])
        print good_json
        output = update_json_row(good_json, entry[0]).close()
        if output is not None:
            print "reprocess " + entry[2]
            print good_json

if __name__ == '__main__':
    main()

