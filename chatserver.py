import json
import threading
import logging
import asyncio
import uuid
import pika
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.resource import Resource, WebSocketApplication

clients = []


class Chat(WebSocketApplication):

    def on_open(self, *args, **kwargs):
        clients.append(self.ws)
        self.userid = uuid.uuid4()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

    def on_close(self, *args, **kwargs):
        clients.remove(self.ws)
        self.connection.close()

    def on_message(self, message, *args, **kwargs):
        if not message: return
        data = json.loads(message)
        data['user'] = self.userid.hex
        self.channel.basic_publish(exchange='logs', routing_key='', body=json.dumps(data))


def start_consumer():
    def callback(ch, method, properties, body):
        for client in clients:
            client.send(json.dumps(json.loads(body)))

    asyncio.set_event_loop(asyncio.new_event_loop())
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(
        exchange='logs',
        exchange_type='fanout')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange='logs',
        queue=queue_name)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True)

    channel.start_consuming()


def index(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html')])
    html = open('index.html', 'rb').read()
    return [html]


application = Resource([
    ('^/chat', Chat),
    ('^/', index)
])


def start_consumer_thread():
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


if __name__ == '__main__':
    start_consumer_thread()
    WSGIServer('{}:{}'.format('0.0.0.0', 8000), application, handler_class=WebSocketHandler).serve_forever()