"""Tool to parse data from Origin IHD device

The device connects to the smart meter and displays usage and cost
information. When connected to a PC via USB it provides a simple web
interface to view the last few month's data.

The web interface presents its data as a bunch of JS files containing
array data. This tool parses the JS and sends the most recent data
using MQTT.
"""
import time
from datetime import datetime, timedelta
import json
import os
import socket
import sys

import pandas as pd
from calmjs.parse import es5
import paho.mqtt.client as mqtt


def parse_data(data):
        tree = es5(data)

        v = tree.children()[0]
        d = v.children()[0]
        parsed = json.loads(str(d.initializer))
        return parsed


def to_series(data):
        series = pd.Series(dtype='float')
        for key, values in data['data'].items():
            base = datetime.fromtimestamp(int(key) / 1000)
            for irec, record in enumerate(values):
                dt = base + timedelta(minutes=30 * irec)
                series[dt] = record
        series = series.sort_index()
        return series


def send(mqtt_host, mqtt_port, mqtt_topic, payload):
    client = mqtt.Client()
    starttime = time.perf_counter()
    while (time.perf_counter() - starttime) < (25 * 60):
        try:
            client.connect(mqtt_host, mqtt_port, 60)
            break
        except socket.error:
            time.sleep(10)
    client.publish(mqtt_topic, json.dumps(payload))
    client.disconnect()


def log_last_to_mqtt(mqtt_host, mqtt_port, mqtt_topic, data):
    # data appears to be 30 minute totals labeled at
    # start of period. So last period will be incomplete.
    # index -2 will be most recently completed 30 min period.
    payload = data.dropna().iloc[-2].to_dict()
    send(mqtt_host, mqtt_port, mqtt_topic, payload)


def load(mount_point):
        data = open(os.path.join(mount_point, "data", "cons.js")).read()
        consumption = to_series(parse_data(data))
        data = open(os.path.join(mount_point, "data", "con_cost.js")).read()
        cost = to_series(parse_data(data))
        data = pd.DataFrame({'consumption': consumption, 'cost': cost})
        return data


def publish(mount_point, mqtt_host, mqtt_port, mqtt_topic):
    log_last_to_mqtt(mqtt_host, mqtt_port, mqtt_topic, load(mount_point))


def display(mount_point):
    data = load(mount_point)
    print(data.dropna())


def cycle_device(mount_point):
    import subprocess, time
    # this is gross - assume in same path as python - fine in a venv..
    script_dir = os.path.dirname(sys.executable)
    script_path = os.path.join(script_dir, 'ihd_power_cycle_usb.sh')
    subprocess.check_call(["sudo", script_path, mount_point])
    # allow time to reconnect
    time.sleep(15)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process energy data from device.')
    parser.add_argument('--print-only', dest='print_only', action='store_true',
                        help='Only print output, don\'t publish')
    parser.add_argument('--no-usb-power-cycle', action='store_true',
                        help='Don\'t power cycle the USB device.')
    parser.add_argument('--mqtt-host', default=os.environ.get('MQTT_HOST'))
    parser.add_argument('--mqtt-port', default=os.environ.get('MQTT_PORT', 1883))
    parser.add_argument('--mqtt-topic', default=os.environ.get('MQTT_TOPIC', "power/usage"))
    parser.add_argument('usb_mount_point', help='Path that the USB device is mounted to')

    args = parser.parse_args()
    
    if args.print_only:
        display(args.usb_mount_point)
    else:
        if args.mqtt_host is None:
            parser.error("--mqtt-host or env var MQTT_HOST are required")

        if not args.no_usb_power_cycle:
            cycle_device(args.usb_mount_point)
        publish(args.usb_mount_point, args.mqtt_host, args.mqtt_port, args.mqtt_topic)


if __name__ == '__main__':
    main()
