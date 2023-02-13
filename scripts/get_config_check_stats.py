#!/usr/bin/env python3
#
import argparse
import datetime
import json
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig

def run():
    description = 'Performs analysis of network config check output file.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_in_file_args(parser)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [dht_success_rate|dht_latency|ls_online|ls_sync|ls_archival|ls_with_init_block] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|count|percent] - REQUIRED')

    parser.add_argument('-K', '--key',
                        required=False,
                        type=str,
                        default=None,
                        dest='key',
                        action='store',
                        help='DHT Server hash OR liteserver key - OPTIONAL')

    cfg = AppConfig(parser.parse_args())

    start_time = datetime.datetime.now()

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    data_length = None
    if data:
        dataset = []
        data = json.loads(data)

        if cfg.args.metric.startswith('ls_'):
            data_length = len(data['liteservers'])
            for element in data['liteservers']:
                if cfg.args.key is not None and cfg.args.key != element['key']:
                    continue
                if cfg.args.metric == 'ls_online':
                    if element['last']:
                        dataset.append(1)
                elif cfg.args.metric == 'ls_archival':
                    if element['is_archival']:
                        dataset.append(1)
                elif cfg.args.metric == 'ls_with_init_block':
                    if element['has_init_block']:
                        dataset.append(1)
                elif cfg.args.metric == 'ls_sync':
                    if element['last']:
                        dataset.append(int(element['last']['ago']))
                else:
                    cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
                    sys.exit(1)

        elif cfg.args.metric.startswith('dht_'):
            data_length = len(data['dht'])
            for element in data['dht']:
                if cfg.args.key is not None and cfg.args.key != element['hash']:
                    continue

                if cfg.args.metric == 'dht_success_rate':
                    dataset.append(element['success_rate'])
                elif cfg.args.metric == 'dht_latency':
                    if element['latency'] is not None:
                        dataset.append(element['latency'])
                else:
                    cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
                    sys.exit(1)
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
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
    elif cfg.args.info == "percent":
        print((len(dataset) / data_length) * 100)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
