#!/usr/bin/env python3
#

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import argparse
import datetime
import Libraries.arguments as ar
import Classes.AppConfig as AppConfig
import Classes.LiteClient as LiteClient
import Classes.TonNetwork as TonNetwork

def run():
    description = 'Runs a method on specified address and returns result.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser, type="ls")
    parser.add_argument('address', nargs=1, help='Blockchain address - REQUIRED')
    parser.add_argument('method', nargs=1, help='Method to run - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())
    lc = LiteClient.LiteClient(cfg.args, cfg.config["liteClient"], cfg.log)
    tn = TonNetwork.TonNetwork(lc, cfg.log)

    start_time = datetime.datetime.now()
    result  = tn.run_method(cfg.args.address[0],cfg.args.method[0])
    runtime = (datetime.datetime.now() - start_time)
    if not result:
        cfg.log.log(os.path.basename(__file__), 1, 'Could not retrieve information.')
        sys.exit(1)
    elif cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

if __name__ == '__main__':
    run()
