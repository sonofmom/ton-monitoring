import os
import json
import Libraries.tools.general as gt

class TonElections:
    def __init__(self, config, log, app_config=None):
        self.config = config
        self.log = log
        self.app_config = app_config

    def query(self, method, payload=None, headers={}):
        if "api_token" in self.config and self.config["api_token"]:
            headers["X-API-Key"] = self.config["api_token"]

        self.log.log(os.path.basename(__file__), 3, "Executing {} query.".format(method))
        try:
            result = gt.send_api_query(
                "{}/{}".format(self.config["url"], method),
                payload=payload,
                headers=headers,
                method='get')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        return result

    def get_last_election(self):
        if self.app_config and hasattr(self.app_config, 'cache_path') and self.app_config.cache_path:
            cache_file = '{}/last_elections.json'.format(self.app_config.cache_path)
            rs = gt.read_cache_file(cache_file, self.app_config.config["caches"]["ttl"]["elections"], self.log)
            if rs:
                return json.loads(rs)

        payload = {
            "return_participants": True,
            "limit": 1,
            "offset": 0
        }
        result = self.query(method='getElections',payload=payload)[0]

        if self.app_config and hasattr(self.app_config, 'cache_path') and self.app_config.cache_path:
            gt.write_cache_file(cache_file, json.dumps(result), self.log)

        return result

    def get_validation_cycles(self, count):
        if self.app_config and hasattr(self.app_config, 'cache_path') and self.app_config.cache_path:
            self.log.log(os.path.basename(__file__), 3, "Cache path detected.")
            cache_file = '{}/validation_cycles_{}.json'.format(self.app_config.cache_path,count)
            rs = gt.read_cache_file(cache_file, self.app_config.config["caches"]["ttl"]["validation_cycles"], self.log)
            if rs:
                return json.loads(rs)

        payload = {
            "return_participants": True,
            "limit": count,
            "offset": 0
        }
        rs = self.query(method='getValidationCycles',payload=payload)

        result = []
        now = gt.get_timestamp()

        for element in rs:
            if element["cycle_info"]["utime_since"] <= now and element["cycle_info"]["utime_until"] >= now:
                element['current'] = True
            else:
                element['current'] = False

            result.append(element)

        if self.app_config and hasattr(self.app_config, 'cache_path') and self.app_config.cache_path:
            gt.write_cache_file(cache_file, json.dumps(result), self.log)

        return result

    def get_current_cycle(self):
        cycles = self.get_validation_cycles(2)
        return next((cycle for cycle in cycles if cycle["current"] is True), None)

# end class
