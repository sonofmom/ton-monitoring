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

import asyncio
import random
from pytonlib import TonlibClient

async def run():
    description = 'Fetches and returns balance of the account.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('address', nargs=1, help='Account address - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    start_time = datetime.datetime.now()
    cfg.log.log(os.path.basename(__file__), 3, "Initializing client")
    loop = asyncio.get_running_loop()
    tonclient = TonlibClient(ls_index=random.randint(0,len(cfg.ls_config["liteservers"])-1),
                          config=cfg.ls_config,
                          keystore=cfg.cache_path,
                          loop=loop)

    await tonclient.init()
    cfg.log.log(os.path.basename(__file__), 3, "Performing account lookup query for '{}'.".format(cfg.args.address[0]))
    try:
        result = await tonclient.generic_get_account_state(cfg.args.address[0])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    await tonclient.close()

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(gt.nt2t(result["balance"]))

if __name__ == '__main__':
    asyncio.run(run())
