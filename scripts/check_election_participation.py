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
    description = "Checks if node is participating in elections.\n" \
                  "Returns delta between current time and election begin if election has begun AND\n" \
                  "node specified is NOT participating. Otherwise 0 is returned."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    cfg.log.log(os.path.basename(__file__), 3, "Executing getElections query.")
    payload = {
        "return_participants": True,
        "limit": 1,
        "offset": 0
    }

    try:
        result = requests.get("{}/getElections".format(cfg.config["elections"]["url"]), payload)
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    if result.ok != True:
        cfg.log.log(os.path.basename(__file__), 1, "Could not retrieve information, code {}".format(result.status_code))
        sys.exit(1)

    election = result.json()[0]

    if election['finished']:
        cfg.log.log(os.path.basename(__file__), 3, "Election is closed")
        print(0)
        sys.exit(0)
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Election is open")

    if next((chunk for chunk in election["participants_list"] if chunk["adnl_addr"] == cfg.args.adnl[0]), None):
        cfg.log.log(os.path.basename(__file__), 3, "Node is participating")
        print(0)
        sys.exit(0)

    cfg.log.log(os.path.basename(__file__), 3, "Node is not participating")
    cfg.log.log(os.path.basename(__file__), 3, "Executing getValidationCycles query.")
    payload = {
        "return_participants": False,
        "limit": 1,
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

    cycle = result.json()
    election["elect_start"] = election["election_id"] - cycle[0]["config15"]["elections_start_before"]

    cfg.log.log(os.path.basename(__file__), 3, "Node is not participating")
    print(gt.get_timestamp() - election["elect_start"])
    sys.exit(0)

if __name__ == '__main__':
    run()
