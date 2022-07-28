#!/usr/bin/env python3
#

import sys
import os
import argparse
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
import Classes.AppConfig as AppConfig
import requests

def run():
    description = "Checks software version of given component. Returns 0 if OK, 1 if outdated, 2 if unknown."
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    parser.add_argument('component', nargs=1, help='Component - REQUIRED')
    parser.add_argument('current_version', nargs=1, help='Current version - REQUIRED')
    cfg = AppConfig.AppConfig(parser.parse_args())

    if cfg.args.component[0] not in ['node']:
        cfg.log.log(os.path.basename(__file__), 3, "Unknown component {}".format(cfg.args.component[0]))
        sys.exit(1)

    versions = get_software_versions(cfg)
    commits = get_github_commits(cfg)
    if cfg.args.current_version[0] in commits and versions[cfg.args.component[0]] in commits:
        if commits.index(cfg.args.current_version[0]) <= commits.index(versions[cfg.args.component[0]]):
            result = 0
        else:
            result = 1
    else:
        cfg.log.log(os.path.basename(__file__), 3, "Some versions could not be found, unknown result")
        result = 2

    print(result)

def get_software_versions(cfg):
    cfg.log.log(os.path.basename(__file__), 3, "Fetching software versions.")
    try:
        rs = requests.get(cfg.config["software_versions"]["url"])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    if rs.ok != True:
        cfg.log.log(os.path.basename(__file__), 1,
                    "Could not retrieve information, code {}".format(rs.status_code))
        sys.exit(1)

    return rs.json()

def get_github_commits(cfg):
    if cfg.cache_path:
        cfg.log.log(os.path.basename(__file__), 3, "Cache path detected.")
        cache_file = '{}/commits_{}.json'.format(cfg.cache_path, cfg.args.component[0])
        rs = gt.read_cache_file(cache_file, cfg.config["caches"]["ttl"]["versions"], cfg.log)
        if rs:
            return json.loads(rs)

    cfg.log.log(os.path.basename(__file__), 3, "Executing version load for {}.".format(cfg.args.component[0]))
    try:
        rs = requests.get(cfg.config["software_versions"]["git_repositories"][cfg.args.component[0]])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    if rs.ok != True:
        cfg.log.log(os.path.basename(__file__), 1,
                    "Could not retrieve information, code {}".format(rs.status_code))
        sys.exit(1)

    data = rs.json()
    result = []
    for element in data:
        result.append(element['sha'])

    if cfg.cache_path:
        cfg.log.log(os.path.basename(__file__), 3, "Storing result to cache.")
        gt.write_cache_file(cache_file, json.dumps(result), cfg.log)

    return result

if __name__ == '__main__':
    run()
