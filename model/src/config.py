from ipaddress import IPv4Address, IPv4Network
from subprocess import check_output
from os import getenv

class Config:
    def __init__(self) -> None:
        self.redis_host = getenv('REDIS_HOST', 'redis')
        self.redis_port = getenv('REDIS_PORT', '6379')

        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'rabbitmq')

        self.hdfs_url = getenv('HDFS_URL', 'hdfs://hdfs-namenode:8020')
        self.traffic_count_data_saving_path = getenv('TRAFFIC_COUNT_DATA_SAVING_PATH', 'processed/data-traffic-count.csv')
        self.traffic_best_model_saving_path = getenv('TRAFFIC_BEST_MODEL_SAVING_PATH', 'weights/best_weights')
        self.hdfs_block_size = getenv('HDFS_BLOCK_SIZE', '1048576')

        self.training_scheduler_exchange_name = getenv('TRAINING_SCHEDULER_EXCHANGE_NAME', 'training_schedule')

        self.spark_master_url = getenv('SPARK_MASTER_URL', 'spark://spark:7077')
        [ self.spark_driver_host ] = filter(
            lambda ip: IPv4Address(ip) in IPv4Network(getenv('SPARK_SUBNET')),
            check_output(['hostname', '-i']).decode(encoding='utf-8').strip().split()
        )
