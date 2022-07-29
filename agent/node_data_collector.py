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
import Libraries.tools.general as gt
import Libraries.arguments as ar
import Classes.AppConfig as AppConfig


def init():
    description = 'Collects information about node and stores it into output JSON'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)

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

    return AppConfig.AppConfig(parser.parse_args())

def run(cfg):
    data = {
        "timestamp": gt.get_timestamp()
    }

    cfg.log.log(os.path.basename(__file__), 3, "Extracting validator engine build info")
    process = subprocess.run([cfg.config["files"]["validator_engine"],"--version"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=15)
    match = re.match(r'.+\[ Commit: (\w+).+', process.stdout.decode("utf-8"), re.M | re.I)
    if match:
        data["validator-engine-version"] = match.group(1)

        versions = gt.get_software_versions(cfg)
        commits = gt.get_github_commits(cfg,'node')
        if versions and commits:
            if data["validator-engine-version"] in commits and versions["node"] in commits:
                if commits.index(data["validator-engine-version"]) <= commits.index(versions["node"]):
                    data["validator-engine-version-check"] = 0
                else:
                    data["validator-engine-version-check"] = 1
            else:
                cfg.log.log(os.path.basename(__file__), 3, "Some versions could not be found, unknown result")
                data["validator-engine-version-check"] = 2

    cfg.log.log(os.path.basename(__file__), 3, "Finding out PID for process '{}'".format(cfg.config["files"]["validator_engine"]))
    data["validator-engine-pid"] = gt.get_process_pid(cfg.config["files"]["validator_engine"])

    cfg.log.log(os.path.basename(__file__), 3, "Extracting number of Signal crashes from main log file '{}'".format(cfg.config["files"]["main_log"]))
    data["statistics"] = {
        "signal_crashes": len(gt.ton_log_tail_n_seek(cfg.config["files"]["main_log"], cfg.args.period, "Signal"))
    }

    cfg.log.log(os.path.basename(__file__), 3, "Collecting number of SLOW ops from thread logs")
    data["statistics"]["slow"] = {}
    for file in glob.glob(cfg.config["files"]["threads_log"]):
        cfg.log.log(os.path.basename(__file__), 3, "Processing file '{}'".format(file))
        slow_count(file, cfg.args.period, data["statistics"]["slow"])

    cfg.log.log(os.path.basename(__file__), 3, "Post processing SLOW counts")
    for element in data["statistics"]["slow"]:
        data["statistics"]["slow"][element]["avg"] = sum(data["statistics"]["slow"][element]["raw"]) / len(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["min"] = min(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["max"] = max(data["statistics"]["slow"][element]["raw"])
        data["statistics"]["slow"][element]["count"] = len(data["statistics"]["slow"][element]["raw"])

    if cfg.args.output:
        cfg.log.log(os.path.basename(__file__), 3, "Writing output to '{}'".format(cfg.args.output))
        f = open(cfg.args.output, "w")
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
    run(init())
