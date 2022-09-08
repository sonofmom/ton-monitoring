#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import Classes.TonIndexer as TonIndexer

def run():
    description = 'Performs analysis of blocks using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_blockchain_base_args(parser)
    ar.set_period_args(parser, 60)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [transactions_load|gas_load|fee_load] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max] - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())
    ti = TonIndexer.TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    data = ti.get_blocks(cfg.args.workchain, cfg.args.shard, cfg.args.period, cfg, with_transactions=True)

    dataset = []
    for element in data:
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
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
        print(0)
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
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
