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

def run():
    description = 'Fetches and returns balance of the account.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('address', nargs=1, help='Account address - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())
    tc = TonHttpApi.TonHttpApi(cfg.config["toncenter"],cfg.log.log)

    start_time = datetime.datetime.now()
    cfg.log.log(os.path.basename(__file__), 3, "Executing getAddressBalance query for address '{}'.".format(cfg.args.address[0]))
    params = {"address": cfg.args.address[0]}
    try:
        result = tc.run_get_method("getAddressBalance", params)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, str(e))
        sys.exit(1)

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(gt.nt2t(int(result["result"])))

if __name__ == '__main__':
    run()
