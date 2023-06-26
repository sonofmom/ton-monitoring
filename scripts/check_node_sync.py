#!/usr/bin/env python3
#

import sys
import os
import argparse
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
from Classes.AppConfig import AppConfig
from Classes.ValidatorConsole import ValidatorConsole

def run():
    description = 'Retrieves node sync status using validator-engine-console.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_console_args(parser)

    cfg = AppConfig(parser.parse_args())
    vc = ValidatorConsole(cfg.args, cfg.config["validatorConsole"], cfg.log)

    start_time = datetime.datetime.now()
    result = vc.getSyncStatus()
    runtime = (datetime.datetime.now() - start_time)

    if result is None:
        cfg.log.log(os.path.basename(__file__), 1, 'Could not retrieve information.')
        sys.exit(1)
    elif cfg.args.get_time:
        print(runtime.microseconds/1000)
    else:
        print(result)

if __name__ == '__main__':
    run()
