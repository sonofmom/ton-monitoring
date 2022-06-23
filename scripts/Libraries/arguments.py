def set_standard_args(parser, type = None):
    parser.add_argument('-c', '--config',
                        required=True,
                        dest='config_file',
                        action='store',
                        help='Script configuration file - REQUIRED')

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3')

    parser.add_argument('-T', '--time',
                        required=False,
                        dest='get_time',
                        const=1,
                        action='store_const',
                        help='Output time required to perform command')

    if type == "ls":
        set_standard_args_ls(parser)

def set_standard_args_ls(parser):
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

def set_standard_args_file(parser):
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

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3')
