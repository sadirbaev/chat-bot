import asyncio
import json
import websockets

CLIENTS = 10
MESSAGES = 10


async def run_client(client):
    async with websockets.connect('ws://localhost:8000/chat') as websocket:
        for message in range(MESSAGES):
            data = {"message": '{}:{}'.format(client, message)}
            await websocket.send(json.dumps(data))
            res = await websocket.recv()
            print(res)

clients = [run_client(client) for client in range(CLIENTS)]
asyncio.get_event_loop().run_until_complete(asyncio.wait(clients))