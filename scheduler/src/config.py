from os import getenv, path


class SchedulerConfig:
    def __init__(self) -> None:
        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
        self.scheduler_exchange_name = getenv(
            'SCHEDULER_EXCHANGE_NAME', 'crawling_schedule')
        self.await_seconds = getenv('AWAIT_SECONDS', '900')
