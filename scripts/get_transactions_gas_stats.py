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
    description = 'Performs analysis of transactions gas usage using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_in_file_args(parser)
    ar.set_transactions_filter_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [gas_per_transaction|gas_usage|gas_per_step] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max] - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    period = data["period"]
    data = ti.filter_transactions(data['data'], cfg.args.filters, cfg.config["params"])

    dataset = []
    for element in data:
        if cfg.args.metric == 'gas_per_transaction':
            if element["compute_gas_used"]:
                dataset.append(element["compute_gas_used"])
            else:
                dataset.append(0)
        elif cfg.args.metric == 'gas_usage':
            limit = None
            if element["compute_gas_limit"]:
                limit = element["compute_gas_limit"]
            elif element["compute_gas_credit"]:
                limit = element["compute_gas_credit"]

            if limit:
                dataset.append(element["compute_gas_used"] / (limit/100))
            else:
                dataset.append(0)
        elif cfg.args.metric == 'gas_per_step':
            if element["compute_gas_used"]:
                dataset.append(element["compute_gas_used"] / element["compute_vm_steps"])
            else:
                dataset.append(0)
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
        print(0)
    elif cfg.args.info == "sum":
        print(sum(dataset))
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
    elif cfg.args.info == "rate":
        result = sum(dataset) / period
    elif cfg.args.info == "min":
        print(min(dataset))
    elif cfg.args.info == "max":
        print(max(dataset))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
