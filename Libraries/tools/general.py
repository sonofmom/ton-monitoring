import os, sys
import time
import socket, struct, random, string
import datetime, re

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

def read_cache_file(cache_file, ttl, log):
    if not check_file_exists(cache_file):
        log.log(os.path.basename(__file__), 3, "Cache file '{}' does not exists".format(cache_file))
        return None

    if ((get_timestamp() - os.path.getctime(cache_file)) > ttl):
        log.log(os.path.basename(__file__), 3, "Cache file '{}' is older then {} seconds!".format(cache_file, ttl))
        return None

    log.log(os.path.basename(__file__), 3, "Loading cache file '{}'".format(cache_file))
    fh = open(cache_file, 'r')
    rs = fh.read()
    fh.close()

    return rs

def write_cache_file(cache_file, content, log):
    log.log(os.path.basename(__file__), 3, "Writing cache file '{}'".format(cache_file))
    tmp = "{}.{}".format(cache_file,''.join(random.choice(string.ascii_letters) for i in range(10)))

    f = open(tmp, "w")
    f.write(content)
    f.close()

    if check_file_exists(cache_file):
        os.unlink(cache_file)

    os.rename(tmp, cache_file)


def ton_log_tail_n_seek(file, time_offset, grep = None):
    result = None
    buffer_size = 8096
    file_size = os.stat(file).st_size

    with open(file) as fh:
        if buffer_size > file_size:
            buffer_size = file_size - 1

        # Find out bytes_offset of lines containing timestamp that
        # is less or equal now() - time_offset
        #
        loop = 0
        bytes_offset = 0
        while True:
            loop += 1
            bytes_offset = file_size - buffer_size * loop
            fh.seek(bytes_offset)
            chunk = fh.read(1024)
            a = get_timestamp() - parse_log_timestamp(chunk).timestamp()
            if (parse_log_timestamp(chunk).timestamp() + time_offset <= get_timestamp()) or fh.tell() == 0:
                break

        fh.seek(bytes_offset)
        lines = fh.readlines()
        lines.pop(0)
        if grep:
            result = [line for line in lines if line.find(grep) > 0]
        else:
            result = lines

    return result


def parse_log_timestamp(line):
    result = None
    match = re.match(r'(?:\n|\r\n?|.)+\[(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d).+', line, re.M | re.I)
    if match:
        result = datetime.datetime.fromisoformat("{}+00:00".format(match.group(1)))

    return result
