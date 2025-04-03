#!/usr/bin/env python3
#
import os
import sys
import argparse
import json
import re
import subprocess
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.tools.general as gt
import Libraries.arguments as ar
from Classes.AppConfig import AppConfig


def init():
    description = 'Collects information about node and stores it into output JSON'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

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

    return AppConfig(parser.parse_args())

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

    data["statistics"] = {}
    cfg.log.log(os.path.basename(__file__), 3, "Parsing main rocksdb stats file '{}/db_stats.txt'".format(cfg.config["files"]["node_db"]))
    data['statistics']['db'] = parse_db_stats("{}/db_stats.txt".format(cfg.config["files"]["node_db"]))

    cfg.log.log(os.path.basename(__file__), 3, "Parsing celldb rocksdb stats file '{}/celldb/db_stats.txt'".format(cfg.config["files"]["node_db"]))
    data['statistics']['celldb'] = parse_db_stats("{}/celldb/db_stats.txt".format(cfg.config["files"]["node_db"]))

    cfg.log.log(os.path.basename(__file__), 3, "Extracting number of Signal crashes from main log file '{}'".format(cfg.config["files"]["main_log"]))
    data["statistics"]["signal_crashes"] = len(gt.ton_log_tail_n_seek(parse_dates(cfg.config["files"]["main_log"]), cfg.args.period, "Signal"))

    if cfg.args.output:
        cfg.log.log(os.path.basename(__file__), 3, "Writing output to '{}'".format(cfg.args.output))
        f = open(cfg.args.output, "w")
        f.write(json.dumps(data))
        f.close()
    else:
        print(json.dumps(data))

def parse_dates(string):
    lt = time.localtime(time.time())
    string = string.replace("##YYYY##", time.strftime("%Y", lt))
    string = string.replace("##MM##", time.strftime("%m", lt))
    string = string.replace("##DD##", time.strftime("%d", lt))
    return string

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

def parse_db_stats(path: str):
    with open(path) as f:
        lines = f.readlines()
    result = {}
    for line in lines:
        s = line.strip().split(maxsplit=1)
        items = re.findall(r"(\S+)\s:\s(\S+)", s[1])
        if len(items) == 1:
            item = items[0]
            if float(item[1]) > 0:
                result[s[0].replace(".", "_")] = float(item[1])
        else:
            if any(float(v) > 0 for k, v in items):
                result[s[0].replace(".", "_")] = {}
                result[s[0].replace(".", "_")] = {k: float(v) for k, v in items}
    return result

if __name__ == '__main__':
    run(init())
