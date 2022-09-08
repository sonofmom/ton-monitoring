import Libraries.tools.general as gt

class TonHttpApi:
    def __init__(self, config, log=None):
        self.config = config
        self.log = log

    def query(self, payload):
        headers = None
        if "api_token" in self.config and self.config["api_token"]:
            headers = {"X-API-Key": self.config["api_token"]}

        try:
            result = gt.send_api_query(
                self.config["url"],
                payload=payload,
                headers=headers,
                method='post')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        return result

    def jsonrpc(self, method, params={}):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1
        }
        return self.query(payload)

# end class
