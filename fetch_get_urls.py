import requests
import sys
from read_get_urls import extract_get_paths
BASE_URL = 'http://dev.datadryad.org'
FILENAME = '/Users/dan/Code/python/dryad_utils/get_urls_for_breaking'

def request_urls(base_url, relative_urls):
    count = 0
    for url in relative_urls:
        url = url.strip()
        absolute_url = base_url + url
        try:
            result = requests.get(absolute_url,verify=False)
            count += 1
            print "%d - %s - %d" % (count, url, result.status_code)
        except Exception as e:
            print "Exception getting %s: %s" % (absolute_url,e.message)
        # now test submissions

if __name__ == '__main__':
    filename = sys.argv[1]
    paths = extract_get_paths(filename)
    request_urls(BASE_URL, paths)
