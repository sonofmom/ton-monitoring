#!/usr/bin/env python3
#

import sys
import os
import argparse
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import requests

def run():
    description = "Checks if node is participating in cycle.\n" \
                  "Returns 0 if not, 1 if yes"
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())

    cfg.log.log(os.path.basename(__file__), 3, "Executing getValidationCycles query.")
    payload = {
        "return_participants": True,
        "limit": 2,
        "offset": 0
    }

    try:
        result = requests.get("{}/getValidationCycles".format(cfg.config["elections"]["url"]), payload)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    if result.ok != True:
        cfg.log.log(os.path.basename(__file__), 1, "Could not retrieve information, code {}".format(result.status_code))
        sys.exit(1)

    cfg.log.log(os.path.basename(__file__), 3, "Looking for active cycle")
    cycle = None
    for element in result.json():
        if element["cycle_info"]["utime_since"] <= gt.get_timestamp() and element["cycle_info"]["utime_until"] >= gt.get_timestamp():
            cycle = element
            continue

    if not cycle:
        cfg.log.log(os.path.basename(__file__), 1, "Could not find active cycle.")
        sys.exit(1)

    if next((chunk for chunk in cycle["cycle_info"]["validators"] if chunk["adnl_addr"] == cfg.args.adnl[0]), None):
        cfg.log.log(os.path.basename(__file__), 3, "Node is participating.")
        print(1)
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Node is not participating.")
        print(0)

    sys.exit(0)

if __name__ == '__main__':
    run()
