import Libraries.tools.general as gt

class TonHttpApi:
    def __init__(self, tc_config, log=None):
        self.tc_config = tc_config
        self.log = log

    def query(self, payload):
        headers = None
        if "api_token" in self.tc_config and self.tc_config["api_token"]:
            headers = {"X-API-Key": self.tc_config["api_token"]}

        try:
            result = gt.send_api_query(
                self.tc_config["url"],
                payload=payload,
                headers=headers,
                method='post')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        return result

    def run_get_method(self, method, params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1
        }
        return self.query(payload)

# end class
