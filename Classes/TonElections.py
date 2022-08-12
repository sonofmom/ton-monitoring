import os
import json
import Libraries.tools.general as gt
import requests
import sys

class TonElections:
    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log

    def get_last_election(self):
        if hasattr(self.cfg, 'cache_path') and self.cfg.cache_path:
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
            result = gt.send_api_query(("{}/getElections".format(self.cfg.config["elections"]["url"])), payload)[0]
        except Exception as e:
            raise Exception("Query failed: {} ".format(str(e)))

        if hasattr(self.cfg, 'cache_path') and self.cfg.cache_path:
            gt.write_cache_file(cache_file, json.dumps(result), self.cfg.log)

        return result

    def get_validation_cycles(self,count):
        if hasattr(self.cfg, 'cache_path') and self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Cache path detected.")
            cache_file = '{}/validation_cycles_{}.json'.format(self.cfg.cache_path,count)
            rs = gt.read_cache_file(cache_file, self.cfg.config["caches"]["ttl"]["validation_cycles"], self.cfg.log)
            if rs:
                return json.loads(rs)

        self.cfg.log.log(os.path.basename(__file__), 3, "Executing getValidationCycles query.")
        payload = {
            "return_participants": True,
            "limit": count,
            "offset": 0
        }

        try:
            rs = requests.get("{}/getValidationCycles".format(self.cfg.config["elections"]["url"]), payload)
        except Exception as e:
            self.cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
            sys.exit(1)

        if rs.ok != True:
            self.cfg.log.log(os.path.basename(__file__), 1,
                        "Could not retrieve information, code {}".format(rs.status_code))
            sys.exit(1)

        result = []
        now = gt.get_timestamp()

        for element in rs.json():
            if element["cycle_info"]["utime_since"] <= now and element["cycle_info"]["utime_until"] >= now:
                element['current'] = True

            result.append(element)

        if self.cfg.cache_path:
            self.cfg.log.log(os.path.basename(__file__), 3, "Storing result to cache.")
            rs = gt.write_cache_file(cache_file, json.dumps(result), self.cfg.log)

        return result

# end class
