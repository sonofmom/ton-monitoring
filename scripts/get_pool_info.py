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
                        help='One of: nominators_count, nominators_balance, validator_balance, total_balance')
    parser.add_argument('addresses', nargs='+', help='One or more pool addresses - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    start_time = datetime.datetime.now()
    cfg.log.log(os.path.basename(__file__), 3, "Initializing client")
    loop = asyncio.get_running_loop()
    tonclient = TonlibClient(ls_index=random.randint(0,len(cfg.ls_config["liteservers"])-1),
                          config=cfg.ls_config,
                          keystore=cfg.cache_path,
                          loop=loop)

    await tonclient.init()

    data = {}
    for address in cfg.args.addresses:
        data[address] = {}
        data[address]["list_nominators"] = await raw_run_method_wrapper(cfg, tonclient, address, "list_nominators")
        data[address]["get_pool_data"] = await raw_run_method_wrapper(cfg, tonclient, address, "get_pool_data")
    await tonclient.close()

    result = 0
    if cfg.args.info == 'nominators_count':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators count")
        for address in data:
            result += len(data[address]["list_nominators"]["stack"][0][1]["elements"])

    elif cfg.args.info == 'nominators_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators balance")
        for address in data:
            result += gt.nt2t(get_pool_nominators_balance(data[address]["list_nominators"]))

    elif cfg.args.info == 'validator_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning validator balance")
        for address in data:
            result += gt.nt2t(get_pool_validator_balance(data[address]["get_pool_data"]))

    elif cfg.args.info == 'total_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning total balance")
        for address in data:
            result += gt.nt2t(get_pool_nominators_balance(data[address]["list_nominators"]))
            result += gt.nt2t(get_pool_validator_balance(data[address]["get_pool_data"]))

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

async def raw_run_method_wrapper(cfg, tonclient, address, method, params=[]):
    cfg.log.log(os.path.basename(__file__), 3, "Performing {} query for '{}'.".format(method, address))
    try:
        rs = await tonclient.raw_run_method(address, method, params)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: {}".format(str(e)))
        sys.exit(1)

    if rs["exit_code"]:
        cfg.log.log(os.path.basename(__file__), 1, "Query exit code: {}".format(rs["exit_code"]))
        sys.exit(1)
    return rs

def get_pool_nominators_balance(data):
    result = 0
    for element in data["stack"][0][1]["elements"]:
        result += int(element["tuple"]["elements"][1]["number"]["number"])
    return result

def get_pool_validator_balance(data):
    return int(data["stack"][3][1], base=16)

if __name__ == '__main__':
    asyncio.run(run())
