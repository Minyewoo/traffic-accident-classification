import json
import time
import uuid
import logging
import sys

import pika
import schedule
from config import SchedulerConfig


def schedule_job(exchange_name):
    config = SchedulerConfig()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.rabbitmq_host))
    channel = connection.channel()

    channel.exchange_declare(
        exchange=exchange_name, exchange_type='fanout')

    schedule_id = uuid.uuid4()
    schedule_info = {'schedule_id': str(schedule_id)}
    message = json.dumps(schedule_info)

    channel.basic_publish(exchange=exchange_name,
                          routing_key='',
                          body=message)

    logging.critical(f' Scheduled: {message}, in {exchange_name}')

    connection.close()


if __name__ == '__main__':
    config = SchedulerConfig()
    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

    schedule \
        .every(int(config.crawling_await_seconds)).seconds \
        .do(lambda: schedule_job(config.clrawling_scheduler_exchange_name))
    
    schedule \
        .every(int(config.processing_await_seconds)).seconds \
        .do(lambda: schedule_job(config.processing_scheduler_exchange_name))

    schedule \
        .every(int(config.training_await_seconds)).seconds \
        .do(lambda: schedule_job(config.training_scheduler_exchange_name))

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        if n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()
