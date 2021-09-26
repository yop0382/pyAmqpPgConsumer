#!/usr/bin/env python3
import pika
import psycopg2
import json

conn = psycopg2.connect(
    host="pgha-postgresql-ha-pgpool",
    database="test",
    user="postgres",
    password="1234",
)

conn.autocommit = True
cur = conn.cursor()


def on_message(channel, method_frame, header_frame, body):
    jbody = json.loads(body.decode('utf-8'))
    print(jbody)
    update_status(jbody["events_id"])
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def update_status(events_id):
    sql = """ UPDATE events SET status = %s WHERE events_id = %s """
    cur.execute(sql, ("done", events_id))
    conn.commit()


connection = pika.BlockingConnection(pika.URLParameters('amqp://postgres:postgres@rbmq-rabbitmq:5672/%2F'))
channel = connection.channel()
channel.basic_qos(prefetch_count=100)
channel.basic_consume('events', on_message)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
