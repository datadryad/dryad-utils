import os
import re
# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D \"%{Age}o\" \"%{GEOIP_COUNTRY_NAME}n_%{GEOIP_REGION}n_%{GEOIP_CITY}n\"" combined

REGEX = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+|\-) "(.*?)" "(.*?)" (\d+) "(.*?)" "(.*?)"'
LINE_REGEX = '([A-Z]*) (.*) (HTTP.*)'

def read_logs(filename):
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

                final_status = matched.group(4)
                response_size = matched.group(5)
                user_agent = matched.group(7)
                time_to_serve = matched.group(8) # in microseconds
                age = matched.group(9)
                geo = matched.group(10)
                row_dict = {
                    'ip' : ip_addr,
                    'date' : request_date,
                    'line' : request_line,
                    'method' : method,
                    'path' : path,
                    'status' : final_status,
                    'size' : response_size,
                    'user_agent' : user_agent,
                    'time' : time_to_serve,
                    'location': geo
                }

if __name__ == '__main__':
    # read_logs(os.path.curdir + '/sample-httplogs')
    read_logs('/Users/dan/temp/dryad-http-logs/bitstreams-datadryad-20130728-20131222')