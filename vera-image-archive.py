#!/usr/bin/env python

"""
Phil Adams http://philadams.net

As always, `-h` is your friend.

Given a .csv file of VERA+ statuses, locally archive all default-sized images.

TODO: hook logging back up to args.verbose and args.quiet
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

    # load config params
    with open(args.config) as f:
        config = json.load(f)
        config['outdir'] = config.get('outdir', './gen')
        if not os.path.exists(config['outdir']):
            os.makedirs(config['outdir'])

    # logging config
    log_level = logging.WARNING  # default
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=logging.WARNING)  # global logging settings
    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    fmt_t = logging.Formatter('%(asctime)s - %(levelname)s:%(name)s:%(message)s')
    log_ch = logging.StreamHandler()
    log_ch.setLevel(logging.DEBUG)  # edit for debugging
    log_ch.setFormatter(fmt)
    log_fh = logging.FileHandler('%s/log.log' % config['outdir'])
    log_fh.setLevel(logging.WARNING)
    log_fh.setFormatter(fmt_t)
    imgdl_log = logging.getLogger('idl-tools.imagearchiver')
    imgdl_log.propagate = False
    imgdl_log.setLevel(logging.DEBUG)
    imgdl_log.addHandler(log_fh)
    imgdl_log.addHandler(log_ch)

    # load all the statuses into memory
    with open(args.statuses, 'rU') as f:
        statuses = [row for row in csv.reader(f)]

    fields = statuses.pop(0)  # header row
    for i, row in enumerate(statuses):
        if i % 25 == 0:
            imgdl_log.info('processing %d/%d' % (i+1, len(statuses)))

        status = dict(zip(fields, row))
        status['img_uri'] = '%s%s' % (config['urlbase'], status['image_path'])
        imgdir = '%s/%s' % (config['outdir'], status['user_id'])
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)

        req = requests.get(status['img_uri'])
        time.sleep(0.1)
        if not req.ok:
            imgdl_log.error('sid%s img http req (%s)' % (status['status_id'],
                                                         status['img_uri']))
            continue
        try:
            img = Image.open(StringIO(req.content))
            img.save('%s/u%s_s%s.jpg' % (imgdir,
                                         status['user_id'],
                                         status['status_id']))
        except IOError as e:
            imgdl_log.error('sid%s img persist (%s)' % (status['status_id'],
                                                          status['img_uri']))
            continue


if '__main__' == __name__:
    main()
