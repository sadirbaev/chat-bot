import asyncio
import json
import websockets
import time 
import datetime

CLIENTS = 1500
MESSAGES = 1


async def run_client(client):
    async with websockets.connect('ws://localhost:8000/chat') as websocket:
        for message in range(MESSAGES):
            data = {"message": '{}:{}'.format(client, message)}
            a = datetime.datetime.now()
            await websocket.send(json.dumps(data))
            await websocket.recv()
            b = datetime.datetime.now()
            if (b-a).microseconds > 1_000_000:
                print(CLIENTS)
            
# while
if True:

    clients = [run_client(client) for client in range(CLIENTS)]
    print(CLIENTS)
    asyncio.get_event_loop().run_until_complete(asyncio.wait(clients))
    print("done")
    time.sleep(3)