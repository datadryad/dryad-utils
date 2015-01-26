import os
import re
from time import strftime, strptime
from dateutil import parser
from item_ids import IDS_TO_HANDLES
# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D \"%{Age}o\" \"%{GEOIP_COUNTRY_NAME}n_%{GEOIP_REGION}n_%{GEOIP_CITY}n\"" combined

REGEX = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+|\-) "(.*?)" "(.*?)" (\d+) "(.*?)" "(.*?)"'
LINE_REGEX = '([A-Z]*) (.*)( HTTP.*)?'
FILENAME_REGEX = '/bitstream\handle/10255/([.^/]*)/([.^/].*)?sequence=(.*)'

def read_logs(filename):
    results = dict()
    all_handles = [x[1] for x in IDS_TO_HANDLES]
    with open(filename,'r') as f:
        for line in f.readlines():
            matched = re.match(REGEX,line)
            if matched == None:
                print line
            else:
                ip_addr = matched.group(1)
                request_date = matched.group(2)
                request_line = matched.group(3)
                request_matched = re.match(LINE_REGEX,request_line)
                method, path = request_matched.group(1), request_matched.group(2)
                # /bitstream/handle/10255/dryad.49967/ROM%2056965_652.g.JPG?sequence=
                path_components = path.split('/')
                if len(path_components) > 5:
                    handle = path_components[4]
                    filename = path_components[5].split('?')[0]
                else:
                    handle = None
                    filename = None
                final_status = matched.group(4)
                response_size = matched.group(5)
                user_agent = matched.group(7)
                time_to_serve = matched.group(8) # in microseconds
                resource_age = matched.group(9)
                geo = matched.group(10)
                # Try to parse the date
                try:
                    parsed_request_date = parser.parse(re.sub('2013:','2013 ',request_date),dayfirst=True)
                except ValueError:
                    parsed_request_date = None # unparseable date
                row_dict = {
                    'apache_ip' : ip_addr,
                    'apache_date' : request_date,
                    'apache_parsed_date' : parsed_request_date.isoformat() if parsed_request_date else None,
                    'request_line' : request_line,
                    'method' : method,
                    'path' : path,
                    'http_status' : final_status,
                    'response_size' : response_size,
                    'user_agent' : user_agent,
                    'apache_time' : time_to_serve,
                    'location': geo,
                    'handle': handle,
                    'filename': filename

                }
                # Only interested in lines for the 101 items
                if handle in all_handles:
                    # this will fail if the timestamp cannot be formatted
                    timestamp = int(parsed_request_date.strftime('%s'))
                    if handle not in results.keys():
                        results[handle] = dict()
                    if parsed_request_date not in results[handle].keys():
                        results[handle][timestamp] = list()
                    results[handle][timestamp].append(row_dict)
    return results

if __name__ == '__main__':
    # read_logs(os.path.curdir + '/sample-httplogs')
    read_logs('/Users/dan/temp/dryad-http-logs/bitstreams-datadryad-20130728-20131222')