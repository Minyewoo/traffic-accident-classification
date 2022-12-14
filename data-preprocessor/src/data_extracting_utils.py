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
