import Libraries.tools.general as gt

import requests
import os

def execute_api_query(cfg, payload, post=False):
    cfg.log.log(os.path.basename(__file__), 3, "Executing zabbix `{}` query.".format(payload["method"]))
    try:
        if post:
            rs = requests.post(cfg.config["zabbix"]["url"], json=payload).json()
        else:
            rs = requests.get(cfg.config["zabbix"]["url"], json=payload).json()
    except Exception as e:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute zabbix query: " + str(e))
        return None

    if "error" in rs:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute zabbix query: {}".format(rs["error"]["data"]))
        return None

    return rs

def fetch_hosts(cfg, groups, tags=None, identifier=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": "extend",
            "groupids": groups,
            "selectGroups": "extend",
            "selectMacros": "extend",
            "selectTags": "extend",
            "selectInterfaces": "extend"
        },
        "auth": cfg.config["zabbix"]["api_token"],
        "id": 1
    }

    if tags is not None:
        payload["params"]["tags"] = []
        for element in tags:
            payload["params"]["tags"].append({"tag": element, "value": tags[element], "operator": 1})

    rs = execute_api_query(cfg, payload)
    if not rs:
        cfg.log.log(os.path.basename(__file__), 1, "Could not fetch host list")
        return None

    if "error" in rs:
        cfg.log.log(os.path.basename(__file__), 1, "Could not execute zabbix query: {}".format(rs["error"]["data"]))
        return None

    if not identifier:
        return rs["result"]
    else:
        result = {}
        for host in rs["result"]:
            macro = next((chunk for chunk in host["macros"] if chunk["macro"] == identifier),
                             None)
            if macro:
                record = {
                    "hostid": host["hostid"],
                    "groups": [],
                    "macros": host["macros"],
                    "tags": host["tags"],
                    "interfaces": host["interfaces"]
                }
                for group in host["groups"]:
                    record["groups"].append(int(group["groupid"]))

                result[macro["value"]] = record
        return result


def update_host(cfg, host, original):
    cfg.log.log(os.path.basename(__file__), 3, "Updating host with ID {}".format(host["hostid"]))

    set_macro(host["macros"], "{$UPDATED}", str(gt.get_timestamp()))

    payload = {
        "jsonrpc": "2.0",
        "method": "host.update",
        "params": {
            "hostid": str(host["hostid"]),
            "status": host["status"],
            "groups": [],
            "tags": host["tags"]
        },
        "auth": cfg.config["zabbix"]["api_token"],
        "id": 1
    }
    for element in host["groups"]:
        if isinstance(element, dict):
            payload["params"]["groups"].append(element)
        else:
            payload["params"]["groups"].append({"groupid": element})

    rs = execute_api_query(cfg, payload)
    if not rs:
        cfg.log.log(os.path.basename(__file__), 1, "Failed to update host with hostid {}".format(host["hostid"]))
        return None

    cfg.log.log(os.path.basename(__file__), 3, "Updating macros")
    for macro in host["macros"]:
        if not "hostmacroid" in macro:
            payload = {
                "jsonrpc": "2.0",
                "method": "usermacro.create",
                "params": {
                    "hostid": str(host["hostid"]),
                    "macro": macro["macro"],
                    "value": macro["value"]
                },
                "auth": cfg.config["zabbix"]["api_token"],
                "id": 1
            }
            rs = execute_api_query(cfg, payload)
            if not rs:
                cfg.log.log(os.path.basename(__file__), 1,
                            "Failed to add macro '{}' with value '{}'".format(macro["macro"],macro["value"]))

        else:
            omacro = next((chunk for chunk in original["macros"] if chunk["hostmacroid"] == macro["hostmacroid"]), None)
            if omacro and omacro["value"] != macro["value"]:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "usermacro.update",
                    "params": {
                        "hostmacroid": str(macro["hostmacroid"]),
                        "value": str(macro["value"])
                    },
                    "auth": cfg.config["zabbix"]["api_token"],
                    "id": 1
                }
                rs = execute_api_query(cfg, payload)
                if not rs:
                    cfg.log.log(os.path.basename(__file__), 1,
                                "Failed to update macro with hostmacroid {}".format(macro["hostmacroid"]))

    return True

def delete_host(cfg, host):
    cfg.log.log(os.path.basename(__file__), 3, "Deleting host with ID {}".format(host["hostid"]))

    payload = {
        "jsonrpc": "2.0",
        "method": "host.delete",
        "params": [host["hostid"]],
        "auth": cfg.config["zabbix"]["api_token"],
        "id": 1
    }

    rs = execute_api_query(cfg, payload)
    if not rs:
        cfg.log.log(os.path.basename(__file__), 1, "Failed to delete host with hostid {}".format(host["hostid"]))
        return None

    return rs

def set_tag(tags, id, value):
    i = next((index for (index, chunk) in enumerate(tags) if chunk["tag"] == id), None)
    if (i):
        tags[i]["value"] = value
    else:
        tags.append({"tag": id, "value": value})

    return tags

def set_macro(macros, id, value):
    i = next((index for (index, chunk) in enumerate(macros) if chunk["macro"] == id), None)
    if i != None:
        macros[i]["value"] = value
    else:
        macros.append({"macro": id, "value": value})

    return macros
