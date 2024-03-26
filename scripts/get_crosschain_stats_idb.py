#!/usr/bin/env python3
#
import sys
import os
import argparse
import datetime
import json
import psycopg
from psycopg.rows import dict_row
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.arguments as ar
import Libraries.tools.general as gt
from Classes.AppConfig import AppConfig

def run():
    description = 'Performs analysis of crosschain blocks statistics using direct access to ton indexer database.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)
    ar.set_standard_args(parser)
    ar.set_config_args(parser)
    ar.set_perf_args(parser)
    ar.set_period_args(parser, 60)

    parser.add_argument('-M', '--metric',
                        required=True,
                        type=str,
                        default=None,
                        dest='metric',
                        action='store',
                        help='Metric to collect [children_latency_min|children_latency_avg|children_latency_max|children_count] - REQUIRED')

    parser.add_argument('-F', '--filters',
                        required=False,
                        type=str,
                        default=None,
                        dest='filters',
                        action='store',
                        help='Filters, comma delimited list of filter rules [skip|include]_[lt|eq|gt]_[value] - OPTIONAL')

    parser.add_argument('-i', '--info',
                        required=True,
                        type=str,
                        default=None,
                        dest='info',
                        action='store',
                        help='Information to output [min|avg|max|sum|rate|count] - REQUIRED')

    cfg = AppConfig(parser.parse_args())
    start_time = datetime.datetime.now()

    dbc = psycopg.connect(
        host=cfg.config["indexer"]["database"]["host"],
        port=cfg.config["indexer"]["database"]["port"],
        dbname=cfg.config["indexer"]["database"]["dbname"],
        user=cfg.config["indexer"]["database"]["credentials_ro"]["user"],
        password=cfg.config["indexer"]["database"]["credentials_ro"]["password"],
        cursor_factory=psycopg.ClientCursor).cursor(row_factory=dict_row)

    db_table = None
    db_field = None

    if cfg.args.metric == 'children_latency_min':
        db_table = 'v_recent_blocks_crosschain_statistics'
        db_field = 'children_latency_min'
    elif cfg.args.metric == 'children_latency_avg':
        db_table = 'v_recent_blocks_crosschain_statistics'
        db_field = 'children_latency_avg'
    elif cfg.args.metric == 'children_latency_max':
        db_table = 'v_recent_blocks_crosschain_statistics'
        db_field = 'children_latency_max'
    elif cfg.args.metric == 'children_count':
        db_table = 'v_recent_blocks_crosschain_statistics'
        db_field = 'children_count'
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown metric requested")
        sys.exit(1)

    sql = """SELECT 
                        {table}.{field} as value 
                    FROM 
                        {table}
                    WHERE 
                        {table}.gen_utime >= %s""".format(table=db_table, field=db_field)

    args = [int(gt.get_datetime_utc(gt.get_timestamp() - cfg.args.period).timestamp())]

    rows = dbc.execute(sql,args).fetchall()

    data = []
    if cfg.args.filters:
        filters = []
        for element in cfg.args.filters.split(','):
            filters.append(element.split('_'))

        for element in rows:
            if filter_record(element, filters) is not None:
                data.append(element)

    else:
        data = rows

    dataset = []
    for element in data:
        if element['value'] is not None:
            dataset.append(element['value'])
        elif cfg.args.metric == 'children_count':
            dataset.append(0)

    runtime = (datetime.datetime.now() - start_time)
    if cfg.args.get_time:
        print(runtime.microseconds / 1000)
    elif len(dataset) == 0:
        print(0)
    elif cfg.args.info == "rate":
        print(sum(dataset) / cfg.args.period)
    elif cfg.args.info == "sum":
        print(sum(dataset))
    elif cfg.args.info == "avg":
        print(sum(dataset) / len(dataset))
    elif cfg.args.info == "min":
        print(min(dataset))
    elif cfg.args.info == "max":
        print(max(dataset))
    elif cfg.args.info == "count":
        print(len(dataset))
    else:
        cfg.log.log(os.path.basename(__file__), 1, "Unknown info requested")
        sys.exit(1)

    sys.exit(0)

def filter_record(record, filters):
    for filter in filters:
        value = record['value']

        match = False
        if filter[1] == 'lt' and value is not None and value < int(filter[2]):
            match = True
        elif filter[1] == 'eq' and value is not None and value == int(filter[2]):
            match = True
        elif filter[1] == 'gt' and value is not None and value > int(filter[2]):
            match = True

        if filter[0] == 'skip' and match or filter[0] == 'include' and not match:
            return None

    return record

if __name__ == '__main__':
    run()
