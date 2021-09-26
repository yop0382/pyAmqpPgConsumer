#!/usr/bin/env python3
import urllib.parse

import pika
import psycopg2
import json


class Consumer:
    conn = None
    pg_connect_string_u = "postgresql://postgres:1234@pgha-postgresql-ha-pgpool:5432/test"
    pg_connect_string = None

    def __init__(self):
        self.pg_connect_string = urllib.parse.urlparse(self.pg_connect_string_u)

    def main(self):
        connection = pika.BlockingConnection(pika.URLParameters('amqp://postgres:postgres@rbmq-rabbitmq:5672/%2F'))
        channel = connection.channel()
        channel.basic_qos(prefetch_count=100)
        channel.basic_consume('events', self.on_message)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        connection.close()

    def on_message(self, channel, method_frame, header_frame, body):
        jbody = json.loads(body.decode('utf-8'))
        print(jbody)
        self.update_status(jbody["events_id"])
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def update_status(self, events_id):
        self.is_connected()
        sql = """ UPDATE events SET status = %s WHERE events_id = %s """
        cur = self.conn.cursor()
        cur.execute(sql, ("done", events_id))

    def is_connected(self):
        try:
            sql = """ SELECT 1 """
            cur = self.conn.cursor()
            cur.execute(sql)
        except:
            self.connect_pg()

    def connect_pg(self):
        username = self.pg_connect_string.username
        password = self.pg_connect_string.password
        database = self.pg_connect_string.path[1:]
        hostname = self.pg_connect_string.hostname
        port = self.pg_connect_string.port

        self.conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )

        self.conn.autocommit = True


if __name__ == '__main__':
    Consumer().main()
