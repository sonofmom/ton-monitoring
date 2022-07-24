import os
import sys
import requests
import json
import Libraries.tools.general as gt

class TonElections:
    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log

    def get_last_election(self):
        if self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Cache path detected.")
            cache_file = '{}/last_elections.json'.format(self.cfg.cache_path)
            rs = gt.read_cache_file(cache_file, self.cfg.config["caches"]["ttl"]["elections"], self.cfg.log)
            if rs:
                return json.loads(rs)

        self.cfg.log.log(os.path.basename(__file__), 3, "Executing getElections query.")
        payload = {
            "return_participants": True,
            "limit": 1,
            "offset": 0
        }

        try:
            result = requests.get("{}/getElections".format(self.cfg.config["elections"]["url"]), payload)
        except Exception as e:
            self.cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
            sys.exit(1)

        if result.ok != True:
            self.cfg.log.log(os.path.basename(__file__), 1,
                        "Could not retrieve information, code {}".format(result.status_code))
            sys.exit(1)

        if self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Storing result to cache.")
            cache_file = '{}/last_elections.json'.format(self.cfg.cache_path)
            rs = gt.write_cache_file(cache_file, json.dumps(result.json()[0]), self.cfg.log)

        return result.json()[0]

    def get_current_cycle(self):
        if self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Cache path detected.")
            cache_file = '{}/current_cycle.json'.format(self.cfg.cache_path)
            rs = gt.read_cache_file(cache_file, self.cfg.config["caches"]["ttl"]["election_cycles"], self.cfg.log)
            if rs:
                return json.loads(rs)

        self.cfg.log.log(os.path.basename(__file__), 3, "Executing getValidationCycles query.")
        payload = {
            "return_participants": True,
            "limit": 2,
            "offset": 0
        }

        try:
            result = requests.get("{}/getValidationCycles".format(self.cfg.config["elections"]["url"]), payload)
        except Exception as e:
            self.cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
            sys.exit(1)

        if result.ok != True:
            self.cfg.log.log(os.path.basename(__file__), 1,
                        "Could not retrieve information, code {}".format(result.status_code))
            sys.exit(1)

        self.cfg.log.log(os.path.basename(__file__), 3, "Looking for active cycle")
        cycle = None
        now = gt.get_timestamp()
        for element in result.json():
            if element["cycle_info"]["utime_since"] <= now and element["cycle_info"][
                "utime_until"] >= now:
                cycle = element
                continue

        if not cycle:
            self.cfg.log.log(os.path.basename(__file__), 1, "Could not find active cycle.")
            sys.exit(1)

        if self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Storing result to cache.")
            cache_file = '{}/current_cycle.json'.format(self.cfg.cache_path)
            rs = gt.write_cache_file(cache_file, json.dumps(cycle), self.cfg.log)

        return cycle

# end class
