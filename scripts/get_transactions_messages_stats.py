#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Libraries.tools.account as at
from Classes.AppConfig import AppConfig
from Classes.TonIndexer import TonIndexer

def run():
    description = 'Performs analysis of transactions messages using ton indexer service.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_in_file_args(parser)
    ar.set_transactions_filter_args(parser)

    parser.add_argument('-M', '--mtype',
                        required=False,
                        type=str,
                        default=None,
                        dest='mtype',
                        action='store',
                        help='Only consider message types [internal|external|crosschain] - OPTIONAL')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [transaction_rate|time_rate|count|e2i_ratio|i2e_ratio] - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    ti = TonIndexer(cfg.config["indexer"], cfg.log)

    start_time = datetime.datetime.now()

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    period = data["period"]
    transactions = ti.filter_transactions(data['data'], cfg.args.filters, cfg.config["params"])

    dataset = {}
    if transactions:
        for element in transactions:
            if element['in_msg']:
                insert_message(message_check(element['in_msg'], cfg.args.mtype), dataset)

            if element['out_msgs']:
                for message in element['out_msgs']:
                    insert_message(message_check(message, cfg.args.mtype), dataset)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif cfg.args.info == "transaction_rate":
        print(len(dataset) / len(transactions))
    elif cfg.args.info == "time_rate":
        print(len(dataset) / period)
    elif cfg.args.info == "count":
        print(len(dataset))
    elif cfg.args.info in ["e2i_ratio","i2e_ratio"]:
        int = 0
        ext = 0
        for element in dataset:
            if dataset[element]['source']:
                int += 1
            else:
                ext += 1
        if int == 0 or ext == 0:
            print(0)
        elif cfg.args.info == "e2i_ratio":
            print (ext/int)
        else:
            print (int/ext)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

def message_check(message, filter):
    if not filter:
        return message

    if filter == 'external' and not message['source']:
        return message
    elif filter == 'internal' and message['source']:
        return message
    elif filter == 'crosschain' and message['source'] and message['destination']:
        src = at.read_friendly_address(message['source'])
        dst = at.read_friendly_address(message['destination'])
        if src['workchain'] != dst['workchain']:
            return message

def insert_message(message, collection):
    if message and message['hash'] not in collection:
        collection[message['hash']] =  message

if __name__ == '__main__':
    run()
