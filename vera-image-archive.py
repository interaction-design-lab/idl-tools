#!/usr/bin/env python

"""
Phil Adams http://philadams.net

As always, `-h` is your friend.

Given a .csv file of VERA+ statuses, locally archive all default-sized images.

TODO: handle network / image saving errors
TODO: intelligent summary log, including errors list
"""

import logging
import os
from StringIO import StringIO
import csv
import json
import time

from pprint import pprint

import requests
from PIL import Image


def main():
    import argparse

    # populate and parse command line options
    parser = argparse.ArgumentParser(description='Image archiving for VERA+')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', default=0)
    group.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('config', help='config params (json)')
    parser.add_argument('statuses', help='veraplus statuses (csv)')
    args = parser.parse_args()

    # logging config
    log_level = logging.WARNING  # default
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # load config params
    with open(args.config) as f:
        config = json.load(f)
        config['outdir'] = config.get('outdir', './gen')

    # load all the statuses into memory
    with open(args.statuses, 'rU') as f:
        statuses = [row for row in csv.reader(f)]

    fields = statuses.pop(0)  # header row
    for row in statuses:
        #sys.stdout.write('\rprocessing row %d...' % i)
        #sys.stdout.flush()

        status = dict(zip(fields, row))
        status['img_uri'] = '%s%s' % (config['urlbase'], status['image_path'])

        req = requests.get(status['img_uri'])
        img = Image.open(StringIO(req.content))

        imgdir = '%s/%s' % (config['outdir'], status['user_id'])
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        img.save('%s/u%s_s%s.jpg' % (imgdir,
                                 status['user_id'],
                                 status['status_id']))

        time.sleep(0.1)
        break


if '__main__' == __name__:
    main()
