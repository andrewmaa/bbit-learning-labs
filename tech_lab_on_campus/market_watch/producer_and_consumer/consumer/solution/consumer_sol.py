from multiprocessing.dummy import connection

import pika
import os
from tech_lab_on_campus.market_watch.producer_and_consumer.consumer.consumer_interface import mqConsumerInterface


class mqConsumer(mqConsumerInterface):
    def __init__(self, binding_key, exchange_name, queue_name):
        self.binding_key = binding_key
        self.exchange_name = exchange_name
        self.queue_name = queue_name

    def setupRMQConnection(self):
        con_params = pika.URLParameters(os.environ["AMQP_URL"])
        connection = pika.BlockingConnection(parameters=con_params)
        channel = connection.channel()
        exchange = channel.exchange_declare(exchange=self.exchange_name)

        channel.queue_declare(queue=self.queue_name)

        channel.queue_bind(
            queue=self.queue_name,
            routing_key=self.binding_key,
            exchange=self.exchange_name,
        )

        channel.basic_consume(
            self.queue_name, on_message_callback=self.callback, auto_ack=False
        )

        

        channel.basic_ack(method_frame.delivery_tag, False)


        channel.start_consuming()


        channel.close()
        connection.close()

