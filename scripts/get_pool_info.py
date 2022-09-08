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
    description = 'Fetches and returns pool information.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='One of: state, nominators_count, nominators_balance, validator_balance, total_balance')

    parser.add_argument('addresses', nargs='+', help='One or more pool addresses - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())
    tc = TonHttpApi.TonHttpApi(cfg.config["http-api"], cfg.log.log)

    start_time = datetime.datetime.now()
    data = {}
    for address in cfg.args.addresses:
        cfg.log.log(os.path.basename(__file__), 3, "Loading data for pool {}".format(address))
        data[address] = {}
        params = {
            "address": address,
            "method": 'list_nominators',
            "stack": []
        }
        cfg.log.log(os.path.basename(__file__), 3, "Loading {}".format(params["method"]))
        try:
            data[address]["list_nominators"] = tc.jsonrpc("runGetMethod", params)
        except Exception as e:
            cfg.log.log(os.path.basename(__file__), 1, str(e))
            sys.exit(1)

        params = {
            "address": address,
            "method": 'get_pool_data',
            "stack": []
        }
        cfg.log.log(os.path.basename(__file__), 3, "Loading {}".format(params["method"]))
        try:
            data[address]["get_pool_data"] = tc.jsonrpc("runGetMethod", params)
        except Exception as e:
            cfg.log.log(os.path.basename(__file__), 1, str(e))
            sys.exit(1)

    result = 0
    if cfg.args.metric == 'state':
        cfg.log.log(os.path.basename(__file__), 3, "Returning pool state")
        result = get_pool_state(data[cfg.args.addresses[0]]["get_pool_data"])

    elif cfg.args.metric == 'nominators_count':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators count")
        for address in data:
            result += len(data[address]["list_nominators"]["result"]["stack"][0][1]["elements"])

    elif cfg.args.metric == 'nominators_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning nominators balance")
        for address in data:
            result += gt.nt2t(get_pool_nominators_balance(data[address]["list_nominators"]))

    elif cfg.args.metric == 'validator_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning validator balance")
        for address in data:
            result += gt.nt2t(get_pool_validator_balance(data[address]["get_pool_data"]))

    elif cfg.args.metric == 'total_balance':
        cfg.log.log(os.path.basename(__file__), 3, "Returning total balance")
        for address in data:
            result += gt.nt2t(get_pool_nominators_balance(data[address]["list_nominators"]))
            result += gt.nt2t(get_pool_validator_balance(data[address]["get_pool_data"]))

    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

def get_pool_nominators_balance(data):
    result = 0
    for element in data["result"]["stack"][0][1]["elements"]:
        result += int(element["tuple"]["elements"][1]["number"]["number"])
    return result

def get_pool_validator_balance(data):
    return int(data["result"]["stack"][3][1], base=16)

def get_pool_state(data):
    return int(data["result"]["stack"][0][1], base=16)

if __name__ == '__main__':
    run()
