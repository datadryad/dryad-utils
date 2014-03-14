from requests.api import request
from item_ids import EMBARGO_1YR, EMBARGO_UAP, EMBARGO_WITH_AVAILABLE, IDS_TO_DOIS
from item_ids import EPERSON_DRYADSTAFF
import requests
from xml.etree import ElementTree
from dateutil import parser, tz
import unicodecsv

BASE_SOLR_URL = "http://datadryad.org/solr/statistics/select/"

class dummy():
    def isoformat(self):
        return ''

def add_items(item_list, items):
    for item in item_list:
        add_item(item,items)

def add_item(item_tuple, items):
    item_id = item_tuple[0]
    embargo_type = item_tuple[1]
    allowed_download_date = item_tuple[2]
    val = {'embargo_type':embargo_type, 'allowed_download_date': allowed_download_date}
    if item_id in items.keys():
        print "Overwriting %s with %s" % (items[item_id], val)
    items[item_id] = val

def main():
    items = dict()
    add_items(EMBARGO_1YR,items)
    add_items(EMBARGO_UAP,items)
    add_items(EMBARGO_WITH_AVAILABLE,items)
    output_list = []
    for item_id in items.keys():
        allowed_download_date = items[item_id]['allowed_download_date']
        embargo_type = items[item_id]['embargo_type']
        options = {'indent':'on','q':'owningItem:' + str(item_id)}
        r = requests.get(BASE_SOLR_URL,params=options)
        try:
            root = ElementTree.fromstring(r.text.encode('utf-8'))
        except UnicodeError as inst:
            print "Unicode error:"
            print inst
            print r.text
            continue
        docs = root.findall('./result/doc');
        for doc in docs:
            doc_dict = extract_downloads(doc)
            if allowed_download_date is not None:
                if allowed_download_date.find('Z') < 0:
                    parsed_embargo = parser.parse(allowed_download_date + 'T00:00:00.000Z')
                else:
                    parsed_embargo = parser.parse(allowed_download_date)
            else:
                parsed_embargo = dummy()
            parsed_download = parser.parse(doc_dict['time'])
            if check_eperson(doc_dict):
                doc_dict['dryad_staff_activity'] = True
            else:
                doc_dict['dryad_staff_activity'] = None
            doc_dict['parsed_download_date'] = parsed_download.isoformat()
            doc_dict['parsed_embargo_date'] = parsed_embargo.isoformat()
            doc_dict['embargo_type'] = embargo_type
            if allowed_download_date:
                doc_dict['downloaded_early'] = parsed_download < parsed_embargo
            inject_dois(item_id, doc_dict)
            output_list.append(doc_dict)
    with open('embargo_report.csv', 'wb') as f:
        allcolumns = []
        for row in output_list:
            allcolumns = allcolumns + row.keys()
        allcolumns = list(set(allcolumns)) # uniquify
        writer = unicodecsv.DictWriter(f,allcolumns)
        writer.writeheader()
        writer.writerows(output_list)

def inject_dois(item_id, doc_dict):
    for doiline in IDS_TO_DOIS:
        if item_id == doiline[0]:
            doc_dict['file_doi'] = doiline[1]
            doc_dict['package_doi'] = doiline[2]

def check_eperson(doc_dict):
    '''
    Returns true if epersonid is in dict and that eperson is dryad staff
    '''
    if 'epersonid' in doc_dict.keys():
        return int(doc_dict['epersonid']) in EPERSON_DRYADSTAFF
    else:
        return False

def lookup_access(xmldoc):
    ''' this needs to get IP addresses from apache logfiles
    '''
    pass

def extract_downloads(xmldoc):
    extracted = dict()
    for child in xmldoc:
        if child.tag == 'arr':
            vals = []
            for val in child:
                vals.append(child.text)
            extracted[child.attrib['name']] = val.text
        else:
            extracted[child.attrib['name']] = child.text
    return extracted

if __name__ == '__main__':
    main()