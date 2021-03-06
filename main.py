#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import signal
import sys
import time

import producer

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

LOGGER.info("__________________________________________")
LOGGER.info("Starting service %s" % time.strftime("%c"))

# general
service_name = "parser"

# arguments
parser = argparse.ArgumentParser(prog=service_name, description='parses web pages and calls API to collect exchange rates')
parser.add_argument('-rmq',      default='localhost',   help='rabbitmq host')
parser.add_argument('-interval', default='300',         help='parsing interval')
args = parser.parse_args()

# RabbitMQ
# rmq_url = 'amqp://guest:guest@'+ args.rmq +':5672/%2F?heartbeat=0'
rmq_url = 'amqp://guest:guest@'+ args.rmq +':5672/%2F'
rmq_exchange = "erp"
rmq_route_logs = "logs"

rmq_client = producer.BlockingProducer(rmq_url, rmq_exchange)

def rqm_send(msg):
    data = {
        "service": service_name,
        "msg": msg
    }
    rmq_client.publish(rmq_route_logs, json.dumps(data))
    LOGGER.info(data)


"""
    Entry point to parser
"""


def finish(signal_num, stack_frame):
    LOGGER.info("Terminating service %s" % time.strftime("%c"))
    rqm_send("Terminating service %s" % time.strftime("%c"))
    rmq_client.close()
    sys.exit()


# handle Termination signal
signal.signal(signal.SIGTERM, finish)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    rqm_send("Starting service with " + str(args))
    counter = 0
    last_sent = time.time()
    while True:
        now = time.time()
        if ((now - last_sent) < float(args.interval)):
            # This can sleep up to 10 seconds
            rmq_client.process_data_events()
        else:
            # Time to send a message
            rqm_send("Executing #" + str(counter))
            counter += 1
            last_sent = time.time()
