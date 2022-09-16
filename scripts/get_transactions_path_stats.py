#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig
from Classes.TonIndexer import TonIndexer

def run():
    description = 'Performs analysis of transactions structure paths using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_blockchain_base_args(parser)
    ar.set_period_args(parser, 60)
    ar.set_transactions_filter_args(parser)

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [count|min|avg|max|sum] - REQUIRED')

    parser.add_argument('-O', '--option',
                        required=False,
                        type=str,
                        default=[],
                        dest='options',
                        action='append',
                        help='Options [nanoton_to_ton] - OPTIONAL')

    parser.add_argument('path', nargs=1, help='Path to extract - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    data = ti.get_transactions(cfg.args.workchain, cfg.args.shard, cfg.args.period, cfg)
    data = ti.filter_transactions(data, cfg.args.filters, cfg.config["params"])

    dataset = []
    for element in data:
        val = gt.get_leaf(element, cfg.args.path[0].split('.'))
        if val is not None:
            dataset.append(val)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif dataset:
        result = 0

        if cfg.args.info == "count":
            result = len(dataset)
        elif cfg.args.info == "sum":
            result = sum(dataset)
        elif cfg.args.info == "avg":
            result = sum(dataset) / len(dataset)
        elif cfg.args.info == "min":
            result = min(dataset)
        elif cfg.args.info == "max":
            result = max(dataset)
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
            sys.exit(1)

        if "nanoton_to_ton" in cfg.args.options:
            result = gt.nt2t(result)

        print(result)
    else:
        print(0)

    sys.exit(0)

if __name__ == '__main__':
    run()
