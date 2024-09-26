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
from Classes.TonIndexerCh import TonIndexerCh

def run():
    description = 'Performs analysis of blocks using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_blockchain_base_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [count] - REQUIRED')

    parser.add_argument('-P', '--period',
                        required=False,
                        type=int,
                        default=60,
                        dest='period',
                        action='store',
                        help='Period to collect - OPTIONAL, defaults to 60')

    parser.add_argument('-O', '--offset',
                        required=False,
                        type=int,
                        default=60,
                        dest='offset',
                        action='store',
                        help='Offset - OPTIONAL, defaults to 60')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|rate|count] - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    start_time = datetime.datetime.now()

    tic = TonIndexerCh(config=cfg.config, log=cfg.log)

    dataset = []
    if cfg.args.metric == 'count':
        count = tic.get_blocks_count(workchain=cfg.args.workchain, period=cfg.args.period, offset=cfg.args.offset)
        for x in range(count):
            dataset.append(1)

    period = cfg.args.period

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
