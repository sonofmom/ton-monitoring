#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import Classes.TonElections as TonElections

def run():
    description = 'Returns current validation cycle information for an address.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('-e', '--exists',
                        required=False,
                        type=int,
                        default=0,
                        dest='exists',
                        action='store',
                        help='Check existence of requested path, return 1 if exists, 0 if not')

    parser.add_argument('adnl', nargs=1, help='ADNL to retrieve - REQUIRED')
    parser.add_argument('path', nargs=1, help='Data path to retrieve - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())
    te = TonElections.TonElections(cfg,cfg.log)
    cycle = te.get_current_cycle()

    if not cycle:
        cfg.log.log(os.path.basename(__file__), 1, "Could not find current validation cycle")
        sys.exit(1)

    cfg.log.log(os.path.basename(__file__), 3, "Looking for ADNL '{}'".format(cfg.args.adnl[0]))
    adnl_data = next((chunk for chunk in cycle["cycle_info"]["validators"] if chunk["adnl_addr"] == cfg.args.adnl[0]), None)
    if not adnl_data:
        cfg.log.log(os.path.basename(__file__), 1, "Data for ADNL '{}' not found".format(cfg.args.adnl[0]))
        if (cfg.args.exists):
            print(0)
            sys.exit(0)
        else:
            sys.exit(1)

    cfg.log.log(os.path.basename(__file__), 3, "Looking for path '{}'".format(cfg.args.path[0]))
    result = gt.get_leaf(adnl_data, cfg.args.path[0].split('.'))

    if result is None:
        cfg.log.log(os.path.basename(__file__), 1, "Path '{}' was not found in data".format(cfg.args.path[0]))
        if cfg.args.exists:
            print(0)
            sys.exit(0)
        else:
            sys.exit(1)
    elif cfg.args.exists:
        print(1)
    elif isinstance(result, bool):
        print(int(result))
    else:
        print(result)

    sys.exit(0)

if __name__ == '__main__':
    run()
