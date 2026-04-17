import pika
import os
from consumer_interface import mqConsumerInterface
from collections import defaultdict

class mqConsumer(mqConsumerInterface):
    def __init__(self, binding_keys, exchange_name, queue_name):
        self.binding_keys = binding_keys if isinstance(binding_keys, list) else [binding_keys]
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.setupRMQConnection()

    def setupRMQConnection(self):
        con_params = pika.URLParameters(os.environ["AMQP_URL"])
        self.connection = pika.BlockingConnection(parameters=con_params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

        self.channel.queue_declare(queue=self.queue_name)

        self.bindQueueToExchange(self.queue_name, self.exchange_name)

        self.channel.basic_consume(
            self.queue_name, on_message_callback=self.on_message_callback, auto_ack=False
        )

    def bindQueueToExchange(self, queueName: str, topic: str):
        for binding_key in self.binding_keys:
            self.channel.queue_bind(
                        queue=queueName,
                        routing_key=binding_key,
                        exchange=topic,
                    )


        
    def on_message_callback(self, channel, method_frame, header_frame, body):
            channel.basic_ack(method_frame.delivery_tag, False)
            print(body.decode('utf-8'))


            channel.close()
            self.connection.close()

    def startConsuming(self):
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def __del__(self):
        print("Closing RMQ connection on destruction")
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception:
             pass
        
        try:
             if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass
