#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
from Classes.AppConfig import AppConfig
from Classes.TonIndexer import TonIndexer

def run():
    description = 'Downloads list of blocks from indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_blockchain_base_args(parser)
    ar.set_period_args(parser, 60)

    parser.add_argument('-o', '--output',
                        required=False,
                        type=str,
                        default=None,
                        dest='output',
                        action='store',
                        help='Write output to indicated file instead of stdout')

    parser.add_argument('-t', '--load-transactions',
                        required=False,
                        type=int,
                        default=1,
                        dest='load_transactions',
                        action='store',
                        help='Load transactions [0|1] OPTIONAL, defaults to 1')

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    result = ti.get_blocks(workchain=cfg.args.workchain,
                               shard=cfg.args.shard,
                               period=cfg.args.period,
                               with_transactions=(cfg.args.load_transactions == 1))

    runtime = (datetime.datetime.now() - start_time)

    dataset = {
        'period': cfg.args.period,
        'data': result
    }

    if cfg.args.output:
        with open(cfg.args.output, 'w') as fd:
            fd.write(json.dumps(dataset))
    else:
        print(json.dumps(dataset))

    if cfg.args.get_time:
        print(runtime.total_seconds())

    sys.exit(0)

if __name__ == '__main__':
    run()
