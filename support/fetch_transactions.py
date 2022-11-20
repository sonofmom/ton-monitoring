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
    description = 'Downloads list of transactions from indexer service.'
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

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    result = ti.get_chain_transactions(workchain=cfg.args.workchain,
                               shard=cfg.args.shard,
                               period=cfg.args.period)

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.output:
        with open(cfg.args.output, 'w') as fd:
            fd.write(json.dumps(result))
    else:
        print(json.dumps(result))

    if cfg.args.get_time:
        print(runtime.total_seconds())

    sys.exit(0)

if __name__ == '__main__':
    run()
