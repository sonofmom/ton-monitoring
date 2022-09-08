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
import Classes.TonHttpApi as TonHttpApi
import Classes.TonIndexer as TonIndexer

def run():
    description = 'Performs analysis of TON Indexer and returns result.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_period_args(parser)
    ar.set_blockchain_base_args(parser)

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=0,
                        dest='info',
                        action='store',
                        help='One of: latency_blocks, missing_blocks')

    cfg = AppConfig.AppConfig(parser.parse_args())
    tc = TonHttpApi.TonHttpApi(cfg.config["http-api"], cfg.log.log)
    ti = TonIndexer.TonIndexer(cfg.config["indexer"], cfg.log.log)

    start_time = datetime.datetime.now()

    cfg.log.log(os.path.basename(__file__), 3, "Fetching consensus block from http api")
    try:
        rs = tc.jsonrpc("getConsensusBlock")
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, str(e))
        sys.exit(1)

    consensus = rs["result"]

    params = {
        "workchain": cfg.args.workchain,
        "shard": cfg.args.shard,
    }
    if cfg.args.info == 'missing_blocks':
        cfg.log.log(os.path.basename(__file__), 3, "Fetching indexed blocks from workchain {} for {}sec".format(cfg.args.workchain, cfg.args.period))
        params["limit"] = 999
        params["sort"] = "asc"
        params["start_utime"] = gt.get_timestamp() - cfg.args.period
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Fetching last known indexed block from workchain {}".format(cfg.args.workchain))
        params["limit"] = 1

    try:
        blocks = ti.query("getBlocksByUnixTime",payload=params)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, str(e))
        sys.exit(1)

    if not len(blocks):
        cfg.log.log(os.path.basename(__file__), 1, "Could not get list of blocks from indexer")
        sys.exit(1)
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Got {} blocks".format(len(blocks)))

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif cfg.args.info == 'latency_blocks':
        print(max(0, int(consensus["consensus_block"]) - blocks[0]["seqno"]))
    elif cfg.args.info == 'missing_blocks':
        last = 0
        missing = 0
        for element in blocks:
            if last and element["seqno"] != last+1:
                missing += 1
            last = element["seqno"]

        print(missing)

if __name__ == '__main__':
    run()
