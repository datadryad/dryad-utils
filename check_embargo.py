from requests.api import request
from item_ids import *
from read_httplogs import read_logs
import requests
from xml.etree import ElementTree
from dateutil import parser, tz
import unicodecsv

BASE_SOLR_URL = "http://datadryad.org/solr/statistics/select/"
LOGS_FILENAME = '/Users/dan/temp/dryad-http-logs/bitstreams-datadryad-20130728-20131222'
class dummy():
    def isoformat(self):
        return ''

def merge_apache_data(output_list):
    apache_logs_dict = read_logs(LOGS_FILENAME)
    all_apache_handles = apache_logs_dict.keys()
    merged_data = list()
    for row in output_list:
        row_handle = row['handle']
        parsed_download_date = row['parsed_download_date_raw']
        unix_time = int(parsed_download_date.strftime('%s'))
        if row_handle in all_apache_handles:
            handle_request_times = apache_logs_dict[row_handle].keys()
            if unix_time in handle_request_times:
                # The solr request time for this handle is in the apache dict, use it directly
                request_time = unix_time
            else:
                # The solr request time is not in the apache dict, find the previous time
                try:
                    request_time = [x for x in handle_request_times if x < unix_time][-1]
                except IndexError:
                    print "unable to find a time for %s prior to %d" % (row_handle, unix_time)
                    request_time = None
            if request_time:
                requests_list = apache_logs_dict[row_handle][request_time]
                if len(requests_list) > 1:
                    print "More than one request for %s at %d", (row_handle, request_time)
                    merged_data.append(row)
                else:
                    request_dict = requests_list[0]
                    merged_row = dict(row.items() + request_dict.items())
                    merged_data.append(merged_row)
            else:
                merged_data.append(row)
        else:
            print "handle %s not found in apache logs" % row_handle
            merged_data.append(row) # bad
    return merged_data

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
            doc_dict['parsed_download_date_raw'] = parsed_download
            doc_dict['parsed_embargo_date'] = parsed_embargo.isoformat()
            doc_dict['embargo_type'] = embargo_type
            if allowed_download_date:
                doc_dict['downloaded_early'] = parsed_download < parsed_embargo
            inject_dois(item_id, doc_dict)
            inject_handles(item_id, doc_dict)
            output_list.append(doc_dict)
    apache_data = merge_apache_data(output_list)
    with open('embargo_report.csv', 'wb') as f:
        allcolumns = []
        for row in apache_data:
            allcolumns = allcolumns + row.keys()
        allcolumns = list(set(allcolumns)) # uniquify
        writer = unicodecsv.DictWriter(f,allcolumns)
        writer.writeheader()
        writer.writerows(apache_data)

def inject_dois(item_id, doc_dict):
    for doiline in IDS_TO_DOIS:
        if item_id == doiline[0]:
            doc_dict['file_doi'] = doiline[1]
            doc_dict['package_doi'] = doiline[2]

def inject_handles(item_id, doc_dict):
    for handle_line in IDS_TO_HANDLES:
        if item_id == handle_line[0]:
            doc_dict['handle'] = handle_line[1]


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