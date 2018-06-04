#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import signal
import sys
import time

import producer


print("__________________________________________")
print("Starting service %s" % time.strftime("%c"))

# general
service_name = "parser"

# arguments
parser = argparse.ArgumentParser(prog=service_name, description='parses web pages and calls API to collect exchange rates')
parser.add_argument('-rmq',      default='localhost',   help='rabbitmq host')
parser.add_argument('-interval', default='300',         help='parsing interval')
args = parser.parse_args()

# RabbitMQ
rmq_url = 'amqp://guest:guest@'+ args.rmq +':5672/%2F?heartbeat=0'
rmq_exchange = "erp"
rmq_route_logs = "logs"

rmq_client = producer.BlockingProducer(rmq_url, rmq_exchange)


def rqm_send(msg):
    data = {
        "service": service_name,
        "msg": msg
    }
    rmq_client.publish(rmq_route_logs, json.dumps(data))
    print(data)



"""
    Entry point to parser
"""


def finish(signal_num, stack_frame):
    print("Terminating service %s" % time.strftime("%c"))
    rqm_send("Terminating service %s" % time.strftime("%c"))
    rmq_client.close()
    sys.exit()


# handle Termination signal
signal.signal(signal.SIGTERM, finish)


if __name__ == "__main__":
    rqm_send("Starting service with " + str(args))
    counter = 0

    while True:
        rqm_send("Executing #" + str(counter))
        counter += 1
        time.sleep(float(args.interval))
