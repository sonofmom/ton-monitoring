#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig

def run():
    description = 'Fetches toncenter msg stats information.'
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


    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output - REQUIRED')

    parser.add_argument('-p', '--period',
                        required=True,
                        type=int,
                        dest='period',
                        action='store',
                        help='Time period in seconds - REQUIRED')

    parser.add_argument('-o', '--period-offset',
                        required=True,
                        type=int,
                        dest='period_offset',
                        action='store',
                        help='Time period offset in seconds - REQUIRED')

    cfg = AppConfig(parser.parse_args())

    period_end_utime = gt.get_timestamp() - cfg.args.period_offset
    period_start_utime = period_end_utime - cfg.args.period

    result = None
    if cfg.args.metric == 'latency':
        try:
            rs = gt.send_api_query(
                "{}msg-latency".format(cfg.config["msg_latency"]["url"]),
                payload={
                    'start_ts': period_start_utime,
                    'end_ts': period_end_utime,
                },
                method='get')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        if cfg.args.info == 'unprocessed_rate':
            result = round(rs['not_processed'] / rs['count'] * 100, 2)
        elif cfg.args.info == 'processed_rate':
            result = round(100 - (rs['not_processed'] / rs['count'] * 100), 2)
        elif cfg.args.info in rs:
            result = rs[cfg.args.info]
        else:
            raise Exception("Unknown info {}".format(cfg.args.info))

    print(result)
    sys.exit(0)

if __name__ == '__main__':
    run()
