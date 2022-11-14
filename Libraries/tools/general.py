from datetime import datetime, timezone
import json
import os
import psutil
import random
import re
import requests
import socket
import string
import struct
import sys
import time
import base64
import shutil
from pathlib import Path


def check_path_exists(path):
    if os.path.exists(path) and os.path.isdir(path) and os.access(path, os.R_OK):
        return True
    else:
        return False


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


def make_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def get_timestamp():
    return round(time.time())


def get_datetime_utc(timestamp=None):
    if not timestamp:
        return datetime.now(timezone.utc)
    else:
        return datetime.fromtimestamp(timestamp, timezone.utc)


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
    tmp = "{}.{}".format(cache_file,ran_string(10))

    with open(tmp, "w") as fd:
        fd.write(content)

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
            chunk = fh.read(buffer_size)
            chunk_ts = parse_log_timestamp(chunk)
            if (chunk_ts and chunk_ts.timestamp() + time_offset <= get_timestamp()) or fh.tell() == 0:
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
        result = datetime.fromisoformat("{}+00:00".format(match.group(1)))

    return result


def get_process_pid(process):
        result = None
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict()
                if pinfo['exe'] == process:
                    result = pinfo['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return result


def send_api_query(url, payload=None, method=None, headers=None):
    try:
        if method == 'post':
            result = requests.post(url, json=payload, headers=headers)
        else:
            result = requests.get(url, params=payload, headers=headers)
    except Exception as e:
        raise Exception("Error: {}".format(str(e)))

    if result.ok != True:
        raise Exception("Code {}".format(result.status_code))

    return result.json()


def get_software_versions(cfg):
    cfg.log.log(os.path.basename(__file__), 3, "Fetching software versions.")
    try:
        result = send_api_query(cfg.config["software_versions"]["url"])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    return result


def get_github_commits(cfg,component):
    if hasattr(cfg, 'cache_path') and cfg.cache_path:
        cache_file = '{}/commits_{}.json'.format(cfg.cache_path, component)
        rs = read_cache_file(cache_file, cfg.config["caches"]["ttl"]["versions"], cfg.log)
        if rs:
            return json.loads(rs)

    cfg.log.log(os.path.basename(__file__), 3, "Executing version load for {}.".format(component))
    try:
        data = send_api_query(cfg.config["software_versions"]["git_repositories"][component])
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute query: " + str(e))
        sys.exit(1)

    result = []
    for element in data:
        result.append(element['sha'])

    if hasattr(cfg, 'cache_path') and cfg.cache_path:
        write_cache_file(cache_file, json.dumps(result), cfg.log)

    return result


def b64_to_hex(b64):
    return base64.b64decode(b64).hex()


def ran_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def archive_file(source, archive_root, subdirs=None, keep_original=False):
    if not isinstance(source, Path):
        file = Path(source)

    if not isinstance(archive_root, Path):
        archive_root = Path(archive_root)

    if not check_path_writable(archive_root):
        raise Exception("Archive root {} does not exist or is not writable".format(archive_root.absolute()))

    if not os.path.exists(source):
        raise Exception("Source file {} does not exist".format(source.absolute()))

    if subdirs:
        for element in subdirs:
            archive_root = archive_root.joinpath(str(element))
            if not os.path.exists(archive_root):
                archive_root.mkdir()

    target = archive_root.joinpath(source.name)

    if keep_original:
        shutil.copyfile(source, target)
    else:
        os.rename(source, target)

def get_file_or_url(source, as_json=False):
    result = None
    if check_file_exists(source):
        with open(source, 'r') as fd:
            result = fd.read()
    else:
        result = requests.get(source).content

    if as_json:
        result = json.loads(result)

    return result


def crop_string(string, length, terminator=""):
    if len(string) <= length:
        return string
    return "{}{}".format(string[0:length-1],terminator)


def unique(data):
    return list(set(data))

