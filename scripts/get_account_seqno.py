#!/usr/bin/env python3
#
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
from Classes.AppConfig import AppConfig
from Classes.TonHttpApi import TonHttpApi

def run():
    description = 'Fetches and returns seqno of the account.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('address', nargs=1, help='Account address - REQUIRED')
    cfg = AppConfig(parser.parse_args())
    tc = TonHttpApi(cfg.config["http-api"],cfg.log.log)

    cfg.log.log(os.path.basename(__file__), 3, "Executing {} method on {}".format("seqno", cfg.config["params"]["config_address"]))
    params = {
        "address": cfg.args.address[0],
        "method": 'seqno',
        "stack": []
    }
    try:
        data = tc.jsonrpc("runGetMethod", params)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, str(e))
        sys.exit(1)

    print (int(data["result"]["stack"][0][1],0))
    sys.exit(0)

if __name__ == '__main__':
    run()
