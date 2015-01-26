from read_httplogs import REGEX, LINE_REGEX
import re
import sys

def read_gets(filename):
    results = list()
    with open(filename,'r') as f:
        for line in f.readlines():
            matched = re.match(REGEX,line)
            if matched == None:
                print line
            else:
                request_date = matched.group(2)
                request_line = matched.group(3)
                request_matched = re.match(LINE_REGEX,request_line)
                method, path = request_matched.group(1), request_matched.group(2)
                results.append({'date': request_date, 'method': method, 'path': path})
    return results

def extract_get_paths(filename):
    results = []
    logs = read_gets(filename)
    skip_strings = ['/bitstream']
    for log in logs:
        if log['method'] == 'GET':
            skip = False
            for skip_string in skip_strings:
                if skip_string in log['path']:
                    skip = True
            if not skip:
                results.append(log['path'])
    return results

if __name__ == '__main__':
    results = extract_get_paths(sys.argv[1])
    for result in results:
        print result

