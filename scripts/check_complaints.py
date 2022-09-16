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
    description = "Checks for passed complaints for a node within given time offset.\n" \
                  "Returns count of complaints"
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')
    parser.add_argument('offset', nargs=1, help='Offset in seconds - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    te = TonElections(cfg.config["elections"], cfg.log, app_config=cfg)

    payload = {
        "adnl_address": cfg.args.adnl[0],
        "limit": 10
    }
    result = te.query(method='getComplaints', payload=payload)

    count = 0
    for element in result:
        if element["created_time"] >= (gt.get_timestamp() - int(cfg.args.offset[0])):
            if element["is_passed"] == True:
                cfg.log.log(os.path.basename(__file__), 3, "Complaint {} is passed.".format(element["hash"]))
                count += 1
            else:
                cfg.log.log(os.path.basename(__file__), 3, "Complaint {} is not passed.".format(element["hash"]))
        else:
            cfg.log.log(os.path.basename(__file__), 3, "Complaint {} is too old to consider.".format(element["hash"]))

    print(count)

if __name__ == '__main__':
    run()
