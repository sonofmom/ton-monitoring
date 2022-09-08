import Libraries.tools.general as gt
import Libraries.tools.account as ac
import json
import os
import re

class TonIndexer:
    def __init__(self, config, log=None):
        self.config = config
        self.log = log

    def query(self, method, payload=None, headers=None):
        if "api_token" in self.config and self.config["api_token"]:
            headers = {"X-API-Key": self.config["api_token"]}

        try:
            result = gt.send_api_query(
                "{}/{}".format(self.config["url"], method),
                payload=payload,
                headers=headers,
                method='get')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        return result

    def get_blocks(self, workchain, shard, period, app_config=None, with_transactions=False):
        data = None
        if app_config and hasattr(app_config, 'cache_path') and app_config.cache_path:
            if with_transactions:
                cache_file = '{}/index_blocks_{}_{}_{}_with_transactions.json'.format(app_config.cache_path, workchain, shard, period)
            else:
                cache_file = '{}/index_blocks_{}_{}_{}.json'.format(app_config.cache_path, workchain, shard, period)

            rs = gt.read_cache_file(cache_file, app_config.config["caches"]["ttl"]["index_blocks"], self.log)
            if rs:
                data = json.loads(rs)

        if not data:
            self.log.log(os.path.basename(__file__), 3, "Fetching blocks from workchain {} shard {} for {}sec".format(workchain, shard, period))
            params = {
                "workchain": workchain,
                "shard": shard,
                "limit": 999,
                "start_utime": gt.get_timestamp() - period
            }
            data = self.query("getBlocksByUnixTime", payload=params)

            if not len(data):
                raise Exception("Could not get list of blocks from indexer")
            else:
                self.log.log(os.path.basename(__file__), 3, "Got {} blocks".format(len(data)))

            if with_transactions:
                self.log.log(os.path.basename(__file__), 3, "Extending blocks with transactions")
                for idx, element in enumerate(data):
                    data[idx]["transactions"] = self.get_block_transactions(element["workchain"], element["shard"], element["seqno"])

            if app_config and hasattr(app_config, 'cache_path') and app_config.cache_path:
                gt.write_cache_file(cache_file, json.dumps(data), self.log)

        return data

    def get_block_transactions(self, workchain, shard, seqno):
        data = None

        self.log.log(os.path.basename(__file__), 3, "Fetching transactions from workchain {} shard {} seqno {} ".format(workchain, shard, seqno))
        params = {
            "workchain": workchain,
            "shard": shard,
            "seqno": seqno
        }
        data = self.query("getTransactionsInBlock", payload=params)

        self.log.log(os.path.basename(__file__), 3, "Got {} transactions".format(len(data)))

        return data

    def get_transactions(self, workchain, shard, period, app_config=None):
        data = None
        if app_config and hasattr(app_config, 'cache_path') and app_config.cache_path:
            cache_file = '{}/index_transactions_{}_{}_{}.json'.format(app_config.cache_path, workchain, shard, period)
            rs = gt.read_cache_file(cache_file, app_config.config["caches"]["ttl"]["index_transactions"], self.log)
            if rs:
                data = json.loads(rs)

        if not data:
            self.log.log(os.path.basename(__file__), 3, "Fetching transactions from workchain {} shard {} for {}sec".format(workchain, shard, period))
            params = {
                "workchain": workchain,
                "shard": shard,
                "limit": 999,
                "start_utime": gt.get_timestamp() - period
            }
            data = self.query("getChainLastTransactions", payload=params)

            if not len(data):
                raise Exception("Could not get list of transactions from indexer")
            else:
                self.log.log(os.path.basename(__file__), 3, "Got {} transactions".format(len(data)))

            if app_config and hasattr(app_config, 'cache_path') and app_config.cache_path:
                gt.write_cache_file(cache_file, json.dumps(data), self.log)

        return data

    def filter_transactions(self, data, filters_input, params):
        if not filters_input:
            return data

        result = []
        filters = []
        for element in filters_input.split(','):
            match = re.search(r'^(skip|include)_(.+)', element, re.MULTILINE)
            if match:
                filters.append( {'op': match.group(1), 'value': match.group(2)} )

        for element in data:
            skip = False
            for filter in filters:
                if filter["value"] == "elector_contract":
                    check = self.is_transaction_member(element, ac.read_friendly_address(params["elector_address"]))
                elif filter["value"] == "system_contract":
                    check = self.is_transaction_member(element, ac.read_friendly_address(params["system_address"]))
                elif filter["value"] == "external":
                    check = self.is_transaction_external(element)
                elif filter["value"] == "failed":
                    check = self.is_transaction_failed(element)
                elif filter["value"] == "compute_skipped":
                    check = self.is_transaction_skipped(element)
                else:
                    check = self.is_transaction_type(element, filter["value"])

                if filter["op"] == "include" and not check:
                    skip = True
                    break
                elif filter["op"] == "skip" and check:
                    skip = True
                    break

            if not skip:
                result.append(element)
                skip = False

        return result


    def is_transaction_type(self, transaction, type):
        if transaction["transaction_type"] == type:
            return True

    def is_transaction_failed(self, transaction):
        if transaction["compute_exit_code"] == None or transaction["compute_exit_code"] > 1:
            return True

    def is_transaction_skipped(self, transaction):
        if transaction["compute_skip_reason"]:
            return True

    def is_transaction_member(self, transaction, address):
        if transaction["account"] == address["raw_form"]:
            return True

        if transaction["in_msg"]:
            if transaction["in_msg"]["source"] == address["bounceable"]["b64"] or transaction["in_msg"]["destination"] == address["bounceable"]["b64"]:
                return True

        if transaction["in_msg"]:
            if transaction["in_msg"]["source"] == address["bounceable"]["b64"] or transaction["in_msg"]["destination"] == address["bounceable"]["b64"]:
                return True

        if next((chunk for chunk in transaction["out_msgs"] if chunk["destination"] == address["bounceable"]["b64"]), None):
            return True

        return False


    def is_transaction_external(self, transaction):
        if transaction["in_msg"] and transaction["in_msg"]["source"] == "":
            return True

        return False



# end class
