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
    description = "Performs analysis of current validation cycle."
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
                        help='Metric to collect [participants|stake|max_factor] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|count] - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    te = TonElections(cfg.config["elections"], cfg.log, app_config=cfg)

    cycle = te.get_current_cycle()
    dataset = []
    if cycle:
        if cfg.args.metric == 'participants':
            dataset.append(int(cycle['cycle_info']['total_participants']))
        else:
            for element in cycle['cycle_info']['validators']:
                if cfg.args.metric == 'stake':
                    dataset.append(gt.nt2t(element['stake']))
                elif cfg.args.metric == 'max_factor':
                    dataset.append(element['max_factor']/65536)
                else:
                    cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
                    sys.exit(1)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Current cycle cannot be loaded")
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


if __name__ == '__main__':
    run()
