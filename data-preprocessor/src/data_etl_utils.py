import pandas as pd


def get_rabbit_queue_messages(connection, queue_name, message_processor=None):
    messages = []
    
    channel = connection.channel()
    queue = channel.queue_declare(queue=queue_name, passive=True)

    if queue.method.message_count == 0:
        return

    for method, properties, body in channel.consume(queue=queue.method.queue, auto_ack=True):
        message = body     
        
        if message_processor is not None:
            message = message_processor(message)
        
        messages.append(message)

        if method.delivery_tag == queue.method.message_count:
            break

    channel.close()

    return messages

def get_redis_records(client, records_ids, record_processor=None):
    records = []

    for id in records_ids:
        record = client.json().get(id)        
        
        if record_processor is not None:
            record = record_processor(record)
        
        records.append(record)

    return records

def save_data_to_hdfs(data, hdfs_url, path, mode='append', header=True):
    data.write.csv(
        f'{hdfs_url}/{path}',
        mode=mode,
        header=header,
    )

def load_data_from_hdfs(spark_session, hdfs_url, path, header=True):
    data = spark_session.read.csv(
        f'{hdfs_url}/{path}',
        header=header,
    )

    return data

def save_data_locally(data, path):
    data.toPandas().to_csv(path, index=False)

def load_local_data(spark_session, path):
    data = pd.read_csv(path)

    return spark_session.createDataFrame(data)
