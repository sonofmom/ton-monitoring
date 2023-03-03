#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig
from Classes.TonElections import TonElections

def run():
    description = 'Returns information for active elections.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to retrieve [participants_count] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|count] - REQUIRED')

    parser.add_argument('-A', '--active',
                        dest='active',
                        action='store_true',
                        help='Only consider active elections')

    cfg = AppConfig(parser.parse_args())
    te = TonElections(cfg.config["elections"], cfg.log, app_config=cfg)
    elections = te.get_last_election()

    if not elections:
        cfg.log.log(os.path.basename(__file__), 1, "Could not fetч last elections")
        sys.exit(1)

    dataset = []
    if cfg.args.active and elections['elect_close'] < gt.get_timestamp():
        cfg.log.log(os.path.basename(__file__), 3, "Active elections requested but last elections are closed")
    else:
        if cfg.args.metric == 'participants_count':
            dataset.append(len(elections['participants_list']))
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)

    if len(dataset) == 0:
        print(0)
    elif cfg.args.info == "sum":
        print(sum(dataset))
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
    elif cfg.args.info == "min":
        print(min(dataset))
    elif cfg.args.info == "max":
        print(max(dataset))
    elif cfg.args.info == "count":
        print(len(dataset))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
