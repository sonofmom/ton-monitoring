# -*- coding: utf-8 -*-
# Description: TON Node data collector
# Author: Swisscops
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import re

from bases.FrameworkServices.SimpleService import SimpleService

priority = 90000

ORDER = [
    'ton_node_sync',
]

CHARTS = {
    'ton_node_sync': {
        'options': [None, 'TON node sync', 'Seconds', 'Sync_status', 'TON_node', 'line'],
        'lines': [
            ['ton_node_sync_mc', 'Last masterchain block ago']
        ]
    }
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.validator_console_bin = self.configuration.get('validator_console_bin')
        self.validator_console_client_key = self.configuration.get('validator_console_client_key', )
        self.validator_console_server_key = self.configuration.get('validator_console_server_key', )
        self.validator_console_node_address = "{}:{}".format(self.configuration.get('validator_console_node_address'), self.configuration.get('validator_console_node_port'))

    @staticmethod
    def check():
        return True

    def get_data(self):
        data = dict()

        output = self.validator_console_exec("getstats")
        node_sync_mc = None
        if output:

            server_time = None
            mc_block_time = None
            match = re.match(r'.+unixtime\s*(\d+).*', output, re.DOTALL)
            if match:
                server_time = match.group(1)

            match = re.match(r'.+masterchainblocktime\s*(\d+).*', output, re.DOTALL)
            if match:
                mc_block_time = match.group(1)

            if server_time and mc_block_time:
                node_sync_mc = int(server_time) - int(mc_block_time)


        data['ton_node_sync_mc'] = node_sync_mc

        return data

    def validator_console_exec(self, cmd):
        args = [self.validator_console_bin,
                "--address", self.validator_console_node_address,
                "--key", self.validator_console_client_key,
                "--pub", self.validator_console_server_key,
                "--verbosity", "0",
                "--cmd", cmd]

        try:
            process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=3)
            return process.stdout.decode("utf-8")
        except Exception as e:
            print("Console execution exception {}".format(str(e)))
            return None


