import logging
import pika


class BlockingProducer(object):
    EXCHANGE_TYPE = "direct"
    EXCHANGE_DURABLE = True

    def __init__(self, url, exchange):
        lf = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
        logging.basicConfig(level=logging.DEBUG, format=lf)
        self._connection = pika.BlockingConnection(pika.URLParameters(url))
        self._channel = self._connection.channel()

        self._exchange = exchange
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type=self.EXCHANGE_TYPE,
            durable=self.EXCHANGE_DURABLE
        )

    def publish(self, route, data):
        self._channel.basic_publish(exchange=self._exchange, routing_key=route, body=data)

    def process_data_events(self, time_limit=10):
        self._connection.process_data_events(time_limit)

    def close(self):
            self._channel.close()
            self._connection.close()
