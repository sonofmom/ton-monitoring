# Overview
TON Node data collector for netdata python.d plugin.

## Metrics
At this moment following metrics are collected:

* Last masterchain block ago

## Installation
* Copy file `ton_node.chart.py` into `/usr/libexec/netdata/python.d/`
* Create file `/etc/netdata/python.d/ton_node.conf` using template provided here, make sure that values defined in the file correspond to your environment
* Activate plugin by adding `ton_node: yes` to `/etc/netdata/python.d.conf` (if file does not exist, initialize it by running `/etc/netdata/edit-config python.d.conf`)
* Restart netdata
