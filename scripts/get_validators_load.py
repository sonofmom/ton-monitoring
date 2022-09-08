#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import json

def run():
    description = 'Retrieves information on validator load using input load json'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_in_file_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to extract, [<key>] - REQUIRED')

    parser.add_argument('adnl', nargs=1, help='ADNL of node - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    cfg.log.log(os.path.basename(__file__), 3, "Looking for ADNL '{}'".format(cfg.args.adnl[0]))
    adnl_data = next((chunk for chunk in data if chunk["adnl_addr"] == cfg.args.adnl[0]), None)
    if not adnl_data:
        cfg.log.log(os.path.basename(__file__), 2, "Data for ADNL '{}' not found".format(cfg.args.adnl[0]))
        sys.exit(1)

    if cfg.args.metric in adnl_data:
        print(adnl_data[cfg.args.metric])
    else:
        cfg.log.log(os.path.basename(__file__), 2, "Metric '{}' not found".format(cfg.args.metric))
        sys.exit(1)

if __name__ == '__main__':
    run()
