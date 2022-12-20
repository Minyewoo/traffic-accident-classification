# while True:
#     pass

import logging
import sys
from config import Config
import pika
from multiprocessing import Process
from modeling import (
    training_job
)

def training_callback(ch, method, properties, body):
    training_job()
    # p = Process(target=training_job)
    # p.start()
    # p.join()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
    config = Config()
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.rabbitmq_host,
            heartbeat=1800,
        )
    )
    channel = connection.channel()
    channel.exchange_declare(
        exchange=config.training_scheduler_exchange_name, exchange_type='fanout')

    queue_info = channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_info.method.queue

    channel.queue_bind(
        exchange=config.training_scheduler_exchange_name, queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=training_callback, auto_ack=True)

    channel.start_consuming()

