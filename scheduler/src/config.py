from os import getenv, path


class SchedulerConfig:
    def __init__(self) -> None:
        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
        self.clrawling_scheduler_exchange_name = getenv(
            'CRAWLING_SCHEDULER_EXCHANGE_NAME', 'crawling_schedule')
        self.processing_scheduler_exchange_name = getenv(
            'PROCESSING_SCHEDULER_EXCHANGE_NAME', 'processing_schedule')
        self.training_scheduler_exchange_name = getenv(
            'TRAINING_SCHEDULER_EXCHANGE_NAME', 'training_schedule')
        self.inference_scheduler_exchange_name = getenv(
            'INFERENCE_SCHEDULER_EXCHANGE_NAME', 'inference_schedule')
        self.crawling_await_seconds = getenv('CRAWLING_AWAIT_SECONDS', '900')
        self.processing_await_seconds = getenv('PROCESSING_AWAIT_SECONDS', '3600')
        self.training_await_seconds = getenv('TRAINING_AWAIT_SECONDS', '3600')
        self.inference_await_seconds = getenv('INFERENCE_AWAIT_SECONDS', '3600')