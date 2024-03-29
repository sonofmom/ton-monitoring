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

def run():
    description = 'Performs analysis of blocks using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_in_file_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [transactions_load|gas_load|fee_load|count|shards] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|rate|count] - REQUIRED')

    cfg = AppConfig(parser.parse_args())

    start_time = datetime.datetime.now()

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    period = data["period"]

    dataset = []
    for element in data["data"]:
        if cfg.args.metric == 'transactions_load':
            dataset.append(len(element["transactions"]))
        elif cfg.args.metric == 'gas_load':
            value = 0
            for transaction in element["transactions"]:
                if transaction["compute_gas_used"]:
                    value += transaction["compute_gas_used"]

            dataset.append(value)
        elif cfg.args.metric == 'fee_load':
            value = 0
            for transaction in element["transactions"]:
                if transaction["fee"]:
                    value += gt.nt2t(transaction["fee"])

            dataset.append(value)
        elif cfg.args.metric == 'count':
            dataset.append(1)
        elif cfg.args.metric == 'shards':
            if element['shard'] not in dataset:
                dataset.append(element['shard'])
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
        print(0)
    elif cfg.args.info == "rate":
        print(sum(dataset) / period)
    elif cfg.args.info == "sum":
        print(sum(dataset))
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
    elif cfg.args.info == "min":
        print(min(dataset))
    elif cfg.args.info == "max":
        print(max(dataset))
    elif cfg.args.info == "count":
        print(len(dataset))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
