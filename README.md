# chat-bot
## chat-bot with gevent + RabbitMQ (pika)
### How to run?
1. Activate source (env)
2. Install requirements
3. Run RabbitMQ server in localhost, use default port(5672) <br>
4. 
- Run chatserver.py without gunicorn in single process
```
python chatserver.py
```
- Run chatserver.py with gunicorn in multi-processes
```
gunicorn -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" -w 4 --bind 0:8000 chatserver
```
&nbsp;&nbsp;&nbsp;<b>Note</b>: makesure, ```gunicorn.conf.py``` file is same directory with chatserver.py. Once worker is initialized, the RabbitMQ consumer starts consuming in the thread. Last but not least, Linux should be used as OS, since gunicorn does not support windows.<br>
&nbsp;&nbsp;&nbsp;5. go to ```localhost:8000```
### Performance measurement
To check the performance of the websocket, run ```benchmark.py```, in my case about 1500 clients send message and recieve in one second. It really depends on how many workers and the numbers of cores of the testing environment.
