import os
import json
import Libraries.tools.general as gt

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

    def get_current_cycle(self):
        if hasattr(self.cfg, 'cache_path') and self.cfg.cache_path:
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
            result = gt.send_api_query(("{}/getValidationCycles".format(self.cfg.config["elections"]["url"])), payload)
        except Exception as e:
            raise Exception("Query failed: {} ".format(str(e)))

        self.cfg.log.log(os.path.basename(__file__), 3, "Looking for active cycle")
        cycle = None
        now = gt.get_timestamp()
        for element in result:
            if element["cycle_info"]["utime_since"] <= now and element["cycle_info"]["utime_until"] >= now:
                cycle = element
                continue

        if not cycle:
            raise Exception("Could not find active cycle.")

        if hasattr(self.cfg, 'cache_path') and self.cfg.cache_path:
            gt.write_cache_file(cache_file, json.dumps(cycle), self.cfg.log)

        return cycle

# end class
