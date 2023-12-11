#!/usr/bin/env python3
#

import sys
import os
import argparse
import json
import time
import copy
import threading
import subprocess
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
from Libraries.tools import general as gt
from Classes.AppConfig import AppConfig
from Classes.LiteClient import LiteClient
from Classes.TonNetwork import TonNetwork

result_stack = {}
def run():
    global result_stack
    description = 'Check status of all lite servers defined in network global configuration file'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)

    parser.add_argument('-o', '--output',
                        required=False,
                        type=str,
                        default=None,
                        dest='output',
                        action='store',
                        help='Write output to indicated file instead of stdout | OPTIONAL')

    parser.add_argument('-m', '--mode',
                        required=False,
                        type=str,
                        default='all',
                        dest='mode',
                        action='store',
                        help='Mode [liteserver|dht|all], defaults to both | OPTIONAL')

    parser.add_argument('-N', '--network-config',
                        required=False,
                        type=str,
                        default=None,
                        dest='network_config',
                        action='store',
                        help='Network global config file | OPTIONAL')

    cfg = AppConfig(parser.parse_args())

    if not cfg.args.network_config:
        cfg.log.log(os.path.basename(__file__), 3, 'Loading Network config file {}'.format(cfg.config['network_config']))
        network_config = gt.send_api_query(cfg.config['network_config'])
        pass
    elif not gt.check_file_exists(cfg.args.network_config):
        cfg.log.log(os.path.basename(__file__), 1, 'Network config file {} does not exist'.format(cfg.args.network_config))
        sys.exit(1)
    else:
        with open(cfg.args.network_config, 'r') as fh:
            cfg.log.log(os.path.basename(__file__), 3, 'Loading Network config file {}'.format(cfg.args.network_config))
            network_config = json.loads(fh.read())

    result = {
        'liteservers': [],
        'dht': []
    }
    if cfg.args.mode in ['all', 'liteservers']:
        cfg.log.log(os.path.basename(__file__), 3, 'Checking {} liteservers using {} threads'.format(len(network_config['liteservers']), cfg.config['limits']['lite_client_threads']))

        queue = copy.deepcopy(network_config['liteservers'])
        resolvers = []
        while queue:
            resolvers = []
            for i in range(0,cfg.config['limits']['lite_client_threads']):
                if queue:
                    th = threading.Thread(target=t_ls_checker, args=(cfg,queue.pop(),network_config))
                    th.start()
                    resolvers.append(th)

            for th in resolvers:
                th.join()

        for element in network_config['liteservers']:
            result['liteservers'].append(result_stack[element['id']['key']])

    cf = '/tmp/{}.json'.format(gt.ran_string(10))
    with open(cf, "w") as fd:
        fd.write(json.dumps(network_config))

    if cfg.args.mode in ['all', 'dht']:
        cfg.log.log(os.path.basename(__file__), 3, 'Checking {} dht servers'.format(len(network_config['dht']['static_nodes']['nodes'])))
        args = [
            cfg.config['dht_ping']['bin'],
            '--global-config', cf,
            '--port', str(cfg.config['dht_ping']['port']),
            "--verbosity", "0"
        ]
        process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=60)
        out = process.stdout.decode("utf-8")
        if out:
            for line in out.splitlines():
                match = re.match(r'(.+) : (\d)/(\d)( \(.+ = )?([\d|\.]+)?', line, re.DOTALL)

                if match:
                    record = {
                        'hash': match.group(1),
                        'answers_received': int(match.group(2)),
                        'queries_sent': int(match.group(3)),
                        'success_rate': 0,
                        'latency': None
                    }

                    if len(match.groups()) == 5 and match.group(5):
                        record['latency'] = float(match.group(5))

                    if record['answers_received']:
                        record['success_rate'] = (record['answers_received'] / record['queries_sent']) * 100

                    result['dht'].append(record)


    os.unlink(cf)

    if cfg.args.output:
        cfg.log.log(os.path.basename(__file__), 3, "Writing output to '{}'".format(cfg.args.output))
        f = open(cfg.args.output, "w")
        f.write(json.dumps(result))
        f.close()
    else:
        print(json.dumps(result))

    sys.exit(0)

def t_ls_checker(cfg, config, network_config):
    global result_stack
    lc = LiteClient(cfg.args, cfg.config["liteClient"], cfg.log, ls_addr="{}:{}".format(gt.dec2ip(config['ip']),config['port']), ls_key=config['id']['key'])
    tn = TonNetwork(lite_client=lc, log=cfg.log)
    result = {
        'key': config['id']['key'],
        'last': lc.last(),
        'is_archival': None,
        'has_init_block': None
    }
    if result['last']:
        result['is_archival'] = tn.check_block_known(blockjson=cfg.config['archival_block'])
        result['has_init_block'] = tn.check_block_known(blockjson=network_config['validator']['init_block'])

    result_stack[result['key']] = result

if __name__ == '__main__':
    run()
