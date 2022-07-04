#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig

import asyncio
import random
from pytonlib import TonlibClient

async def run():
    description = 'Fetches and returns pool information.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=0,
                        dest='info',
                        action='store',
                        help='One of: nominators_count, nominators_balance')
    parser.add_argument('address', nargs=1, help='Pool address - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    start_time = datetime.datetime.now()
    cfg.log.log(os.path.basename(__file__), 3, "Initializing client")
    loop = asyncio.get_running_loop()
    keystore = "/tmp/pytonlib"
    try:
        keystore = gt.mk_utemp(keystore)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not fetch user temp: " + str(e))
        sys.exit(1)

    tonclient = TonlibClient(ls_index=random.randint(0,len(cfg.ls_config["liteservers"])-1),
                          config=cfg.ls_config,
                          keystore=keystore,
                          loop=loop)

    await tonclient.init()
    cfg.log.log(os.path.basename(__file__), 3, "Performing list_nominators query for '{}'.".format(cfg.args.address[0]))
    try:
        rs = await tonclient.raw_run_method(cfg.args.address[0], 'list_nominators', [])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: {}".format(str(e)))
        sys.exit(1)

    if rs["exit_code"]:
        cfg.log.log(os.path.basename(__file__), 1, "Query exit code: {}".format(rs["exit_code"]))
        sys.exit(1)

    await tonclient.close()

    result = 0
    if cfg.args.info == 'nominators_count':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators count")
        result = len(rs["stack"][0][1]["elements"])
    elif cfg.args.info == 'nominators_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators balance")
        for element in rs["stack"][0][1]["elements"]:
            result += gt.nt2t(element["tuple"]["elements"][1]["number"]["number"])

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

if __name__ == '__main__':
    asyncio.run(run())
