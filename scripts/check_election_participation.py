#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import Classes.TonElections as TonElections

def run():
    description = "Checks if node is participating in elections.\n" \
                  "Returns delta between current time and election begin if election has begun AND\n" \
                  "node specified is NOT participating. Otherwise 0 is returned."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())
    te = TonElections.TonElections(cfg.config["elections"], cfg.log, app_config=cfg)

    election = te.get_last_election()

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

    cycle = te.get_current_cycle()
    election["elect_start"] = election["election_id"] - cycle["config15"]["elections_start_before"]

    cfg.log.log(os.path.basename(__file__), 3, "Node is not participating")
    print(gt.get_timestamp() - election["elect_start"])
    sys.exit(0)

if __name__ == '__main__':
    run()
