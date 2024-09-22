import Libraries.tools.general as gt
import Libraries.tools.account as ac
import json
import os
import clickhouse_connect
import re

class TonIndexerCh:
    def __init__(self, config, log=None):
        self.config = config
        self.dbc = None
        if "clickhouse" in self.config:
            if "credentials_ro" in self.config["clickhouse"]:
                self.dbc = clickhouse_connect.get_client(
                    host=self.config["clickhouse"]["host"],
                    port=self.config["clickhouse"]["port"],
                    secure=self.config["clickhouse"]["secure"],
                    verify=self.config["clickhouse"]["verify"],
                    username=self.config["clickhouse"]["credentials_ro"]["user"],
                    password=self.config["clickhouse"]["credentials_ro"]["password"],
                    database=self.config["clickhouse"]["dbname"]
                )

        self.log = log
        if not self.dbc:
            raise Exception("Database connection is either not defined or invalid")

    def get_shards(self, seqno=None, as_tree=False):
        if seqno:
            sql = "select * from shard_state final where mc_seqno={};".format(seqno)
        else:
            sql = "select * from shard_state final where mc_seqno=(select max(mc_seqno) as mc_tip from shard_state final);"

        rs = self.dbc.query(sql)
        if rs.result_rows:
            data = gt.dict_by_map(rs.result_rows, rs.column_names)
            if as_tree:
                result = {}
                for element in data:
                    if element['workchain'] not in result:
                        result[element['workchain']] = {}

                    if element['shard'] not in result[element['workchain']]:
                        result[element['workchain']][element['shard']] = element
                return result
            else:
                return data

    def get_block(self, workchain, shard, seqno):
        sql = "select * from blocks final where workchain={} and shard={} and seqno={};".format(workchain,shard,seqno)
        rs = self.dbc.query(sql)
        if rs.result_rows:
            return gt.dict_by_map(rs.result_rows, rs.column_names)[0]

# end class
