#!/usr/bin/env python3
#

import sys
import os
import argparse
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Classes.Logger import Logger
import Libraries.tools.general as gt

def init():
    description = 'Returns values of SLOW messages in TON Node log file(s) within given time range'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    parser.add_argument('-f', '--file',
                        required=True,
                        dest='file',
                        action='store',
                        help='File or directory containing files - REQUIRED')

    parser.add_argument('-r', '--range',
                        required=True,
                        type=int,
                        dest='range',
                        action='store',
                        help='Time range to consider, in seconds - REQUIRED')

    parser.add_argument('-n', '--name',
                        required=True,
                        type=str,
                        dest='name',
                        action='store',
                        help='Name of Timer subsystem - REQUIRED')

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - Default: 0')

    parser.add_argument('-m', '--metric',
                        required=False,
                        type=str,
                        default='avg',
                        dest='metric',
                        action='store',
                        help='Metric min/max/avg - Default: avg')

    args = parser.parse_args()
    log = Logger(args.verbosity)

    log.log(os.path.basename(__file__), 3, "Checking file or directory '{}'".format(args.file))
    if not os.path.exists(args.file):
        log.log(os.path.basename(__file__), 1, "Data file or directory '{}' does not exist!".format(args.file))
        sys.exit(1)

    return args, log

def run(args, log):
    files = []
    if os.path.isfile(args.file):
        log.log(os.path.basename(__file__), 3, "Adding file '{}' to stack".format(args.file))
        files.append(args.file)
    else:
        for filename in os.listdir(args.file):
            fqfn = os.path.join(args.file, filename)
            if os.path.isfile(fqfn):
                log.log(os.path.basename(__file__), 3, "Adding file '{}' to stack".format(fqfn))
                files.append(fqfn)

    if len(files) == 0:
        log.log(os.path.basename(__file__), 1, "No files to process")
        sys.exit(1)

    result = 0
    stack = []
    for file in files:
        stack += process_file(file, args, log)

    if stack:
        if args.metric == 'avg':
            result = sum(stack) / len(stack)
        elif args.metric == 'max':
            result = max(stack)
        elif args.metric == 'min':
            result = min(stack)

    print(result)

def process_file(file, args, log):
    log.log(os.path.basename(__file__), 3, "Processing file '{}'".format(file))
    result = []

    lines = gt.ton_log_tail_n_seek(file, args.range, "SLOW")
    if lines:
        for line in lines:
            match = re.match(r'.+\[name:{}\]\[duration:(\d+\.*\d*)ms\]'.format(args.name), line, re.M | re.I)
            if match:
                result.append(float(match.group(1)))

    return result

if __name__ == '__main__':
    run(*init())
