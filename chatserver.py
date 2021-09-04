import json
import threading
import logging
import uuid
import pika
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.resource import Resource, WebSocketApplication

class PikaMassenger():

    def __init__(self, *args, **kwargs):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange='logs', 
            exchange_type='fanout')

    def consume(self, callback):
        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(
            exchange='logs', 
            queue=queue_name)

        self.channel.basic_consume(
            queue=queue_name, 
            on_message_callback=callback, 
            auto_ack=True)

        self.channel.start_consuming()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()


class Chat(WebSocketApplication):

    def on_open(self, *args, **kwargs):
        self.userid = uuid.uuid4()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')
        consumer_thread = threading.Thread(target=start_consumer, args=[self,])
        consumer_thread.start()
        

    def on_close(self, *args, **kwargs):
        self.connection.close()

    def on_message(self, message, *args, **kwargs):
        if not message: return
        data = json.loads(message)
        data['user'] = self.userid.hex
        self.channel.basic_publish(exchange='logs', routing_key='', body=json.dumps(data))


    def on_broadcast(self, data):
        self.ws.send(json.dumps(data))

def start_consumer(socket):
    def callback(ch, method, properties, body):
        socket.on_broadcast(json.loads(body))
        
    with PikaMassenger() as consumer:
        consumer.consume(callback=callback)


def index(environ, start_response):
    start_response('200 OK', [('Content-type','text/html')])
    html = open('index.html', 'rb').read()
    return [html]


application = Resource([
    ('^/chat', Chat),
    ('^/', index)
])


if __name__ == '__main__':
    WSGIServer('{}:{}'.format('0.0.0.0', 8000), application, handler_class=WebSocketHandler).serve_forever()