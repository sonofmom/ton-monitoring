#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
from Classes.AppConfig import AppConfig
from Classes.TonElections import TonElections

def run():
    description = "Returns number of consecutive cycles node did NOT participate in."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('-n', '--number',
                        required=False,
                        type=int,
                        default=5,
                        dest='number',
                        action='store',
                        help='Number of past cycles to check')

    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    te = TonElections(cfg.config["elections"], cfg.log, app_config=cfg)

    cycles = te.get_validation_cycles(cfg.args.number)
    cycles.reverse()

    result = 0

    for element in cycles:
        if next((chunk for chunk in element["cycle_info"]["validators"] if chunk["adnl_addr"] == cfg.args.adnl[0]), None):
            result = 0
        else:
            result += 1

    print(result)
    sys.exit(0)

if __name__ == '__main__':
    run()
