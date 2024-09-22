#!/usr/bin/env python3
#
import json
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig
from Classes.TonIndexerCh import TonIndexerCh

def run():
    description = "Outputs current latency vs masterchain using ClickHouse indexer DB."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_blockchain_base_args(parser)
    cfg = AppConfig(parser.parse_args())

    tic = TonIndexerCh(config=cfg.config, log=cfg.log)
    shards = tic.get_shards(as_tree=True)
    if shards and cfg.args.workchain in shards and cfg.args.shard in shards[cfg.args.workchain]:
        shard = shards[cfg.args.workchain][cfg.args.shard]
        shard_block = tic.get_block(workchain=shard['workchain'],shard=shard['shard'],seqno=shard['seqno'])
        print(shard['mc_block_gen_utime'] - shard_block['gen_utime'])

if __name__ == '__main__':
    run()
