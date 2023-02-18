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
    description = "Fetches validators telemetry from TON GLASS Server"
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
                        help='Metric to retrieve - REQUIRED')

    cfg = AppConfig(parser.parse_args())

    rs = gt.send_api_query("{}/{}".format(cfg.config['glass']['url'], '/statistics/validators/telemetry_statistics'))

    if cfg.args.metric in rs:
        print(rs[cfg.args.metric])
        sys.exit(0)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
        sys.exit(1)

if __name__ == '__main__':
    run()
