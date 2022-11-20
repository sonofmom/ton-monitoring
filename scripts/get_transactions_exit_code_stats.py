#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig
from Classes.TonIndexer import TonIndexer

def run():
    description = 'Performs analysis of transactions exit codes using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_in_file_args(parser)
    ar.set_transactions_filter_args(parser)

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [rate|count|percentage] - REQUIRED')

    parser.add_argument('-C', '--codes',
                        required=True,
                        type=str,
                        default=None,
                        dest='codes',
                        action='store',
                        help='Comma delimited "OR" list of exit codes to consider, int or range in [start:end] format - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    period = data[0]["utime"] - data[-1]["utime"]
    data = ti.filter_transactions(data, cfg.args.filters, cfg.config["params"])

    dataset = []
    codes = ar.parse_range_param(cfg.args.codes)
    for element in data:
        if element["compute_exit_code"] in codes:
            dataset.append(element)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
        print(0)
    elif cfg.args.info == "rate":
        print(len(dataset) / period)
    elif cfg.args.info == "count":
        print(len(dataset))
    elif cfg.args.info == "percentage":
        print(len(dataset) / (len(data) / 100))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
