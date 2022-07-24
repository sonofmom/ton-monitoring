#!/usr/bin/env python3
#

import sys
import os
import argparse
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Classes.Logger import Logger
import Libraries.tools.general as gt

def init():
    description = 'Returns PID of a process by name'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - Default: 0')

    parser.add_argument('process', nargs=1, help='Process - REQUIRED')
    args = parser.parse_args()
    log = Logger(args.verbosity)
    return args, log

def run(args, log):
    result = None
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict()
           if args.process[0] == pinfo['exe']:
               result = pinfo['pid']
               break
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass

    print(result)

if __name__ == '__main__':
    run(*init())
