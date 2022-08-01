#!/usr/bin/env python3
#

import sys
import os
import argparse
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Classes.AppConfig as AppConfig
import Classes.LiteClient as LiteClient
import Classes.TonNetwork as TonNetwork

def run():
    description = 'Checks if lite server finds the block, returns 1 if known and 0 if not.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser, type="ls")
    parser.add_argument('blockinfo', nargs=1, help='Block information - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())
    lc = LiteClient.LiteClient(cfg.args, cfg.config["liteClient"], cfg.log)
    tn = TonNetwork.TonNetwork(lc, cfg.log)

    start_time = datetime.datetime.now()
    result  = tn.check_block_known(cfg.args.blockinfo[0])
    runtime = (datetime.datetime.now() - start_time)
    if result is None:
        cfg.log.log(os.path.basename(__file__), 1, 'Could not retrieve information.')
        sys.exit(1)
    elif cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

if __name__ == '__main__':
    run()
