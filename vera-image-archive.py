#!/usr/bin/env python

"""
Phil Adams http://philadams.net

As always, `-h` is your friend. Given a db details file with
authentication credentials and a list of `user_id` values, locally
archive the images.
"""

import logging
import json
from pprint import pprint

import MySQLdb


def main():
    import argparse

    # populate and parse command line options
    parser = argparse.ArgumentParser(description='Image archiving for VERA+')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', default=0)
    group.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('dbdeets', help='db credentials and user_id values')
    args = parser.parse_args()

    # logging config
    log_level = logging.WARNING  # default
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # connect to the db
    with open(args.dbdeets) as f:
        dbdeets = json.load(f)
    conn = MySQLdb.connect(host=dbdeets['db']['hostname'],
                           user=dbdeets['db']['username'],
                           passwd=dbdeets['db']['password'],
                           db=dbdeets['db']['dbname'])
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    print cursor

    # SELECT STATEMENT
    users_q= """
        select *
        from users u
        where
            u.study_id>=%d""" % (100)
    cursor.execute(users_q)
    users = cursor.fetchall()
    print len(users)
    print users[0]

if '__main__' == __name__:
    main()
