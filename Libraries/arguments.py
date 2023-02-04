def set_config_args(parser):
    parser.add_argument('-c', '--config',
                        required=True,
                        dest='config_file',
                        action='store',
                        help='Script configuration file - REQUIRED')

def set_standard_args(parser):
    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - OPTIONAL, default: 0')

def set_perf_args(parser):
    parser.add_argument('-T', '--time',
                        required=False,
                        dest='get_time',
                        const=1,
                        action='store_const',
                        help='Output time required to perform command - OPTIONAL')

def set_liteserver_args(parser):
    parser.add_argument('-a', '--addr',
                        required=True,
                        dest='ls_addr',
                        action='store',
                        help='LiteServer address:port - REQUIRED')

    parser.add_argument('-b', '--b64',
                        required=True,
                        dest='ls_key',
                        action='store',
                        help='LiteServer base64 key as encoded in network config - REQUIRED')


def set_in_file_args(parser):
    parser.add_argument('-f', '--file',
                        required=True,
                        dest='file',
                        action='store',
                        help='File containing data - REQUIRED')

    parser.add_argument('-m', '--maxage',
                        required=False,
                        type=int,
                        default=300,
                        dest='maxage',
                        action='store',
                        help='Maximum age of data file in seconds - OPTIONAL')

def set_blockchain_base_args(parser):
    parser.add_argument('-w', '--workchain',
                        required=False,
                        type=int,
                        default=-1,
                        dest='workchain',
                        action='store',
                        help='Workchain - OPTIONAL, default: -1')

    parser.add_argument('-s', '--shard',
                        required=False,
                        type=int,
                        default=None,
                        dest='shard',
                        action='store',
                        help='Shard - OPTIONAL')

def set_period_args(parser, default_value=300):
    parser.add_argument('-p', '--period',
                        required=False,
                        type=int,
                        default=default_value,
                        dest='period',
                        action='store',
                        help='Load data for last X seconds - OPTIONAL, default: {}'.format(default_value))

def set_transactions_filter_args(parser):
    parser.add_argument('-F', '--filter',
                        required=False,
                        type=str,
                        default=None,
                        dest='filters',
                        action='store',
                        help='Filters, comma delimited list of filter rules [skip|include]_[elector|failed|<transaction_type>] - OPTIONAL')

def parse_range_param(param):
    result = []
    for element in param.split(','):
        if ':' not in element:
            element = int(element)
            if element not in result:
                result.append(int(element))
        else:
            parts = element.split(':')
            for i in range(int(parts[0]),int(parts[1])+1):
                if i not in result:
                    result.append(i)

    return result
