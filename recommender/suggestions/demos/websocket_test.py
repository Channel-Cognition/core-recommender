import asyncio
import json
import websockets

async def send_test_data(uri, convo_id, data):
    async with websockets.connect(uri) as websocket:
        # Connect to the WebSocket server
        await websocket.send(json.dumps({"type": "connect", "convo_id": convo_id}))

        # Simulate sending data to the server
        await websocket.send(json.dumps({"type": "send_data", "data": data}))

        # Receive and print the response from the server
        response = await websocket.recv()
        print(f"Received from server: {response}")

# Replace 'ws://localhost:8000/ws/result/' with your WebSocket URL
websocket_uri = 'ws://localhost:8000/ws/result/'
conversation_id = '216518a8-8ec7-465d-8e01-27832db51bd6'  # Replace with your conversation ID
test_data = {'key': 'value'}  # Replace with the data you want to send

asyncio.get_event_loop().run_until_complete(send_test_data(websocket_uri, conversation_id, test_data))
