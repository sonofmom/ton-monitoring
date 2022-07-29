#!/usr/bin/env python3
#

import sys
import os
import argparse
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Classes.AppConfig as AppConfig
import Classes.LiteClient as LiteClient
import Classes.TonNetwork as TonNetwork
import Classes.TonElections as TonElections

def run():
    description = 'Fetches validators load statistics from blockchain, maps it to ADNL and returns JSON'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('-o', '--output',
                        required=False,
                        type=str,
                        default=None,
                        dest='output',
                        action='store',
                        help='Write output to indicated file instead of stdout')
    parser.add_argument('period', nargs=1, help='Max period to fetch, in seconds - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())
    lc = LiteClient.LiteClient(cfg.args, cfg.config["liteClient"], cfg.log)
    tn = TonNetwork.TonNetwork(lc, cfg.log)
    te = TonElections.TonElections(cfg, cfg.log)

    vdata = te.get_current_cycle()
    if not vdata:
        cfg.log.log(os.path.basename(__file__), 1, "Could not find active validation cycle")
        sys.exit(1)

    cfg.log.log(os.path.basename(__file__), 3, 'Calculating maximum possible period for current cycle')
    t_now = int(time.time())
    t_max = t_now - vdata["cycle_info"]["utime_since"]
    t_period = int(cfg.args.period[0])
    cfg.log.log(os.path.basename(__file__), 3, '{} - {} = {} seconds'.format(t_now,vdata["cycle_info"]["utime_since"],t_max))
    if t_period > t_max:
        t_period = t_max

    cfg.log.log(os.path.basename(__file__), 3, 'Using period of {} seconds'.format(t_period))
    cfg.log.log(os.path.basename(__file__), 3, 'Fetching validators load from blockchain')
    result = tn.get_validators_load((t_now-t_period),t_now)

    cfg.log.log(os.path.basename(__file__), 3, 'Mapping ADNLs to PUBKEYS for result')
    for i in range(len(result)):
        record = next((chunk for chunk in vdata["cycle_info"]["validators"] if chunk["pubkey"] == result[i]["pubkey"]),
                         None)
        if record:
            result[i]["adnl_addr"] = record["adnl_addr"]

    if not result:
        cfg.log.log(os.path.basename(__file__), 1, 'Could not retrieve information.')
        sys.exit(1)
    elif cfg.args.output:
        cfg.log.log(os.path.basename(__file__), 3, "Writing output to '{}'".format(cfg.args.output))
        f = open(cfg.args.output, "w")
        f.write(json.dumps(result))
        f.close()
    else:
        print(json.dumps(result))

if __name__ == '__main__':
    run()
