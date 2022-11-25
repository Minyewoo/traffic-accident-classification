import json
import time
import uuid
import logging
import sys

import pika
import schedule
from config import SchedulerConfig


def schedule_job():
    config = SchedulerConfig()

    crawling_id = uuid.uuid4()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.rabbitmq_host))
    channel = connection.channel()

    channel.exchange_declare(
        exchange=config.scheduler_exchange_name, exchange_type='fanout')

    crawling_id = uuid.uuid4()
    schedule_info = {'schedule_id': str(crawling_id)}
    message = json.dumps(schedule_info)

    channel.basic_publish(exchange=config.scheduler_exchange_name,
                          routing_key='',
                          body=message)

    logging.critical(f' Scheduled: {message}')

    connection.close()


if __name__ == '__main__':
    config = SchedulerConfig()
    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

    schedule.every(int(config.await_seconds)).seconds.do(schedule_job)

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        if n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()
