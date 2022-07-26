#!/usr/bin/env python3
#

import os
import sys
import argparse
import json
import re
import glob
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from Classes.Logger import Logger
import Libraries.tools.general as gt

def init():
    description = 'Collects information about node and stores it into output JSON'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    parser.add_argument('-c', '--config',
                        required=True,
                        dest='config_file',
                        action='store',
                        help='Script configuration file - REQUIRED')

    parser.add_argument('-p', '--period',
                        required=True,
                        type=int,
                        dest='period',
                        action='store',
                        help='Period to consider when parsing logs, in seconds - REQUIRED')

    parser.add_argument('-o', '--output',
                        required=False,
                        dest='output',
                        action='store',
                        help='File to write result - OPTIONAL')

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - Default: 0')

    args = parser.parse_args()
    log = Logger(args.verbosity)

    log.log(os.path.basename(__file__), 3, 'Configuration file {}'.format(args.config_file))
    if not gt.check_file_exists(args.config_file):
        log.log(os.path.basename(__file__), 1, "Configuration file does not exist!")
        sys.exit(1)
    try:
        fh = open(args.config_file, 'r')
        cfg = json.loads(fh.read())
        fh.close()
    except Exception as e:
        log.log(os.path.basename(__file__), 1, "Configuration file read error: {}".format(str(e)))
        sys.exit(1)

    return cfg, args, log

def run(cfg, args, log):
    data = {
        "timestamp": gt.get_timestamp()
    }


    log.log(os.path.basename(__file__), 3, "Extracting validator engine build info")
    process = subprocess.run([cfg["files"]["validator_engine"],"--version"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=15)
    match = re.match(r'.+\[ Commit: (\w+).+', process.stdout.decode("utf-8"), re.M | re.I)
    if match:
        data["validator-engine-version"] = match.group(1)

    log.log(os.path.basename(__file__), 3, "Finding out PID for process '{}'".format(cfg["files"]["validator_engine"]))
    data["validator-engine-pid"] = gt.get_process_pid(cfg["files"]["validator_engine"])

    log.log(os.path.basename(__file__), 3, "Finding out PID for process '{}'".format(cfg["files"]["validator_engine"]))
    data["validator-engine-pid"] = gt.get_process_pid(cfg["files"]["validator_engine"])

    log.log(os.path.basename(__file__), 3, "Extracting number of Signal crashes from main log file '{}'".format(cfg["files"]["main_log"]))
    data["statistics"] = {
        "signal_crashes": len(gt.ton_log_tail_n_seek(cfg["files"]["main_log"], args.period, "Signal"))
    }

    log.log(os.path.basename(__file__), 3, "Collecting number of SLOW ops from thread logs")
    data["statistics"]["slow"] = {}
    for file in glob.glob(cfg["files"]["threads_log"]):
        log.log(os.path.basename(__file__), 3, "Processing file '{}'".format(file))
        slow_count(file, args.period, data["statistics"]["slow"])

    log.log(os.path.basename(__file__), 3, "Post processing SLOW counts")
    for element in data["statistics"]["slow"]:
        data["statistics"]["slow"][element]["avg"] = sum(data["statistics"]["slow"][element]["raw"]) / len(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["min"] = min(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["max"] = max(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["count"] = len(data["statistics"]["slow"][element]["raw"])

    if args.output:
        log.log(os.path.basename(__file__), 3, "Writing output to '{}'".format(args.output))
        f = open(args.output, "w")
        f.write(json.dumps(data))
        f.close()
    else:
        print(json.dumps(data))

def slow_count(file, period, data):
    lines = gt.ton_log_tail_n_seek(file, period)
    if lines:
        for line in lines:
            match = re.match(r'.+\[name:(\w+)\]\[duration:(\d+\.*\d*)ms\]', line, re.M | re.I)
            if match:
                subsys = match.group(1)
                if subsys not in data:
                    data[subsys] = {"raw": []}
                data[subsys]["raw"].append(float(match.group(2)))

if __name__ == '__main__':
    run(*init())
