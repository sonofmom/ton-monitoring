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
    description = 'Collects statistics of validators load using input load json'
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
                        help='Metric to collect, [online|offline|<key>] - REQUIRED')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [count|percentage|min|avg|max|sum] - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())

    data = gt.read_cache_file(cfg.args.file, cfg.args.maxage, cfg.log)
    if data:
        data = json.loads(data)
    else:
        cfg.log.log(os.path.basename(__file__), 1, "File {} does not exist or is older then {} seconds".format(cfg.args.file, cfg.args.maxage))
        sys.exit(1)

    dataset = []
    for element in data:
        if cfg.args.metric == 'online':
            if element['online']:
                dataset.append(element)
        elif cfg.args.metric == 'offline':
            if not element['online']:
                dataset.append(element)
        elif cfg.args.metric in element:
            dataset.append(element[cfg.args.metric])
        else:
            cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
            sys.exit(1)

    if len(dataset) == 0:
        print(0)
    elif cfg.args.info == "count":
        print(len(dataset))
    elif cfg.args.info == "percentage":
        print(len(dataset) / (len(data) / 100))
    elif cfg.args.info == "sum":
        print(sum(dataset))
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
    elif cfg.args.info == "min":
        print(min(dataset))
    elif cfg.args.info == "max":
        print(max(dataset))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
