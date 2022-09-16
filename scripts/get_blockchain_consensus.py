#!/usr/bin/env python3
#

import sys
import os
import argparse
import datetime
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig
from Classes.TonHttpApi import TonHttpApi

def run():
    description = 'Fetches and returns latest consensus block using toncenter.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)

    parser.add_argument('-m', '--metric',
                        required=False,
                        type=str,
                        default='block',
                        dest='metric',
                        action='store',
                        help='Metric type, one of block|time|age|rate. Default value: block')

    cfg = AppConfig(parser.parse_args())
    tc = TonHttpApi(cfg.config["http-api"], cfg.log.log)

    start_time = datetime.datetime.now()
    cfg.log.log(os.path.basename(__file__), 3, "Executing getConsensusBlock.")
    try:
        rs = tc.jsonrpc("getConsensusBlock")
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, str(e))
        sys.exit(1)
    runtime = (datetime.datetime.now() - start_time)

    if cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        if cfg.args.metric == 'time':
            print(int(rs["result"]["timestamp"]))
        elif cfg.args.metric == 'age':
            result = time.mktime(datetime.datetime.now().timetuple()) - rs["result"]["timestamp"]
            if result < 0:
                result = 0
            print(result)
        elif cfg.args.metric == 'rate':
            rate = 0
            if hasattr(cfg, 'cache_path') and cfg.cache_path:
                rate_file = '{}/rate_file.json'.format(cfg.cache_path)
                cfg.log.log(os.path.basename(__file__), 3, "Checking for presence of rate file '{}'.".format(rate_file))
                if gt.check_file_exists(rate_file):
                    cfg.log.log(os.path.basename(__file__), 3,"Loading and parsing file '{}'.".format(rate_file))
                    try:
                        fh = open(rate_file, 'r')
                        prev_result = json.loads(fh.read())
                        fh.close()

                        seconds = time.mktime(datetime.datetime.now().timetuple()) - prev_result["result"]["timestamp"]
                        blocks = rs["result"]["consensus_block"] - prev_result["result"]["consensus_block"]
                        if blocks and seconds:
                            rate = blocks / seconds

                    except Exception as e:
                        cfg.log.log(os.path.basename(__file__), 1, "Could not load and parse rate file: {}".format(str(e)))
                else:
                    cfg.log.log(os.path.basename(__file__), 3, "File not found.")

                try:
                    fh = open(rate_file, 'w')
                    fh.write(json.dumps(rs, indent=4, sort_keys=True))
                    fh.close()
                except Exception as e:
                    cfg.log.log(os.path.basename(__file__), 1, "Could not write rate file: {}".format(str(e)))

            print(rate)
        else:
            print(int(rs["result"]["consensus_block"]))

if __name__ == '__main__':
    run()
