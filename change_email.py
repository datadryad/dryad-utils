#!/usr/bin/env python

# Change a user's email address and reindex their items.

__author__ = 'daisie'

import os
import re
import sys
from sql_utils import dict_from_query, execute_sql_query, rows_from_query, list_from_query

if __name__ == '__main__':
    user_spec = raw_input('Enter the user ID or email address: ')
    is_user_id = re.match("\d+", user_spec)
    if is_user_id is not None:
        user_dict = dict_from_query("select * from eperson where eperson_id = %s;" % (user_spec))
    else:
        user_dict = dict_from_query("select * from eperson where email = '%s';" % (user_spec))
    if user_dict is not None:
        user_id = user_dict['eperson_id']
    else:
        print "Did not find a matching eperson"
        sys.exit()
    print "Current email address is: %s" % (user_dict['email'])
    new_address = raw_input('Enter the new email address: ')
    execute_sql_query("update eperson set email = '%s' where eperson_id = %s;" % (new_address, user_id))
    items = rows_from_query('select item_id from item where submitter_id = %s;' % (user_id))
    for item in items[1:len(items)-1]:
        statement = "bash /opt/dryad/bin/dspace update-discovery-index -i %s" % (item[0])
        print statement
        os.system(statement)
    print "All done!"
