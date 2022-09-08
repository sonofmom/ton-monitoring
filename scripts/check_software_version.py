#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig

def run():
    description = "Checks software version of given component. Returns 0 if OK, 1 if outdated, 2 if unknown."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('component', nargs=1, help='Component - REQUIRED')
    parser.add_argument('current_version', nargs=1, help='Current version - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    if cfg.args.component[0] not in ['node']:
        cfg.log.log(os.path.basename(__file__), 3, "Unknown component {}".format(cfg.args.component[0]))
        sys.exit(1)

    versions = gt.get_software_versions(cfg)
    commits = gt.get_github_commits(cfg,cfg.args.component[0])
    if cfg.args.current_version[0] in commits and versions[cfg.args.component[0]] in commits:
        if commits.index(cfg.args.current_version[0]) <= commits.index(versions[cfg.args.component[0]]):
            result = 0
        else:
            result = 1
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Some versions could not be found, unknown result")
        result = 2

    print(result)

if __name__ == '__main__':
    run()
