import os
import time
import sys, socket, struct

def check_path_writable(path):
    if os.path.exists(path) and os.path.isdir(path) and os.access(path, os.W_OK):
        return True
    else:
        return False

def check_file_exists(file):
    if os.path.exists(file) and os.path.isfile(file) and os.access(file, os.R_OK):
        return True
    else:
        return False

def check_file_writable(file):
    if os.path.exists(file) and os.path.isfile(file) and os.access(file, os.W_OK):
        return True
    else:
        return False

def get_datetime_string(timestamp=time.time()):
    return time.strftime("%d.%m.%Y %H:%M:%S %Z", time.localtime(timestamp))

def get_timestamp():
    return round(time.time())


def get_leaf(data, path):
    result = None
    if isinstance(data, dict):
        if path[0] in data:
            result = data[path[0]]

    elif isinstance(data, list):
        if path[0].isnumeric():
            if len(data) > int(path[0]):
                result = data[int(path[0])]

    if result is not None:
        if len(path) > 1:
            result = get_leaf(result, path[1:])

    return result

def dec2ip(value):
    return socket.inet_ntoa(struct.pack('>i', int(value)))

def ip2dec(value):
    return struct.unpack('>i',socket.inet_aton(value))[0]

def nt2t(tons):
    return int(tons)/10**9

def console_log(message):
    print("{}: {}".format(get_datetime_string(time.time()), message))
