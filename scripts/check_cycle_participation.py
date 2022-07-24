#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Classes.AppConfig as AppConfig
import Classes.TonElections as TonElections

def run():
    description = "Checks if node is participating in cycle.\n" \
                  "Returns 0 if not, 1 if yes"
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('adnl', nargs=1, help='ADNL address of node - REQUIRED')

    cfg = AppConfig.AppConfig(parser.parse_args())
    te = TonElections.TonElections(cfg, cfg.log)

    cycle = te.get_current_cycle()

    if next((chunk for chunk in cycle["cycle_info"]["validators"] if chunk["adnl_addr"] == cfg.args.adnl[0]), None):
        cfg.log.log(os.path.basename(__file__), 3, "Node is participating.")
        print(1)
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Node is not participating.")
        print(0)

    sys.exit(0)

if __name__ == '__main__':
    run()
