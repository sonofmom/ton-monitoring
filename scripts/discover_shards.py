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
    description = "Outputs list of shards active on MC block using ClickHouse Indexer."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('-S', '--seqno',
                        required=False,
                        type=int,
                        default=None,
                        dest='seqno',
                        action='store',
                        help='Masterchain Seqno - OPTIONAL')

    cfg = AppConfig(parser.parse_args())

    tic = TonIndexerCh(config=cfg.config, log=cfg.log)
    shards = tic.get_shards(seqno=cfg.args.seqno)

    if shards:
        print(json.dumps(shards, indent=4))

if __name__ == '__main__':
    run()
