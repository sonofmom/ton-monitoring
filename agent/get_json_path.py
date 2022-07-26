#!/usr/bin/env python3
#

import os
import sys
import argparse
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Classes.Logger import Logger
import Libraries.tools.general as gt

def init():
    description = 'Reads JSON file, extracts path and returns its value'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - Default: 0')

    parser.add_argument('file', nargs=1, help='File to read - REQUIRED')
    parser.add_argument('path', nargs=1, help='Path to return - REQUIRED')

    args = parser.parse_args()
    log = Logger(args.verbosity)

    log.log(os.path.basename(__file__), 3, 'File {}'.format(args.file[0]))
    if not gt.check_file_exists(args.file[0]):
        log.log(os.path.basename(__file__), 1, "File does not exist!")
        sys.exit(1)
    try:
        fh = open(args.file[0], 'r')
        data = json.loads(fh.read())
        fh.close()
    except Exception as e:
        log.log(os.path.basename(__file__), 1, "File read error: {}".format(str(e)))
        sys.exit(1)

    return data, args, log

def run(data, args, log):
    result = gt.get_leaf(data,args.path[0].split('.'))
    if result is None:
        sys.exit(1)
    else:
        print(result)

if __name__ == '__main__':
    run(*init())
