import asyncio
import json
import websockets
from nats.aio.client import Client as NATS

clients = set()


# ==========================
# WS HANDLER (FIXED)
# ==========================
async def ws_handler(websocket):
    clients.add(websocket)
    print("Client connected")

    try:
        async for message in websocket:
            # Try to parse as JSON for item recognition data
            try:
                data = json.loads(message)
                if data.get('type') == 'item_recognized':
                    print("\n" + "=" * 60)
                    print("VISUAL ACUITY - ITEM RECOGNIZED:")
                    print(f"  Item: {data.get('display')}")
                    print(f"  Answer: {data.get('answer')}")
                    print(f"  User Answer: {data.get('userAnswer')}")
                    print(f"  Size: {data.get('size')}px")
                    print(f"  Size Group: {data.get('sizeGroup')}")
                    print(f"  Category: {data.get('category')}")
                    print(f"  Distance: {data.get('distance')}cm")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Response Time: {data.get('responseTime')}ms")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'face_not_detected':
                    print("\n" + "=" * 60)
                    print("FACE NOT DETECTED:")
                    print(f"  Distance: {data.get('distance')}cm")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'ishihara_answer':
                    print("\n" + "=" * 60)
                    print("ISHIHARA TEST - ANSWER:")
                    print(f"  Plate Number: {data.get('plateNumber')}")
                    print(f"  Expected: {data.get('expected')}")
                    print(f"  User Answer: {data.get('userAnswer')}")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Distance: {data.get('distance')}cm")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'ishihara_complete':
                    print("\n" + "=" * 60)
                    print("ISHIHARA TEST - COMPLETE:")
                    print(f"  Total Plates: {data.get('totalPlates')}")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Score: {data.get('score')}%")
                    print(f"  Diagnosis: {data.get('diagnosis')}")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'contrast_answer':
                    print("\n" + "=" * 60)
                    print("CONTRAST TEST - ANSWER:")
                    print(f"  Step: {data.get('step')}")
                    print(f"  Letters Shown: {data.get('lettersShown')}")
                    print(f"  User Answer: {data.get('userAnswer')}")
                    print(f"  Contrast: {data.get('contrast')}")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Distance: {data.get('distance')}cm")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'contrast_complete':
                    print("\n" + "=" * 60)
                    print("CONTRAST TEST - COMPLETE:")
                    print(f"  Step Score: {data.get('stepScore')}%")
                    print(f"  Chart Score: {data.get('chartScore')}%")
                    print(f"  Combined Score: {data.get('combinedScore')}%")
                    print(f"  Diagnosis: {data.get('diagnosis')}")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'amsler_complete':
                    print("\n" + "=" * 60)
                    print("AMSLER TEST - COMPLETE:")
                    print(f"  Left Eye Issue: {data.get('leftEyeIssue')}")
                    print(f"  Right Eye Issue: {data.get('rightEyeIssue')}")
                    print(f"  Marks Count: {data.get('marksCount')}")
                    print(f"  Score: {data.get('score')}%")
                    print(f"  Diagnosis: {data.get('diagnosis')}")
                    print(f"  Notes: {data.get('notes')}")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'tritan_answer':
                    print("\n" + "=" * 60)
                    print("TRITAN TEST - ANSWER:")
                    print(f"  Round: {data.get('round')}")
                    print(f"  Target Shape: {data.get('targetShape')}")
                    print(f"  User Answer: {data.get('userAnswer')}")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Distance: {data.get('distance')}cm")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'tritan_complete':
                    print("\n" + "=" * 60)
                    print("TRITAN TEST - COMPLETE:")
                    print(f"  Total Rounds: {data.get('totalRounds')}")
                    print(f"  Correct: {data.get('correct')}")
                    print(f"  Score: {data.get('score')}%")
                    print(f"  Diagnosis: {data.get('diagnosis')}")
                    print("=" * 60 + "\n")
                elif data.get('type') == 'hue_complete':
                    print("\n" + "=" * 60)
                    print("HUE TEST - COMPLETE:")
                    print(f"  Accuracy: {data.get('accuracy')}%")
                    print(f"  TES Score: {data.get('tesScore')}")
                    print(f"  Diagnosis: {data.get('diagnosis')}")
                    print(f"  Distance: {data.get('distance')}cm")
                    print("=" * 60 + "\n")
            except json.JSONDecodeError:
                pass  # Not JSON, ignore

    except websockets.ConnectionClosed:
        print("Client disconnected")

    finally:
        clients.remove(websocket)


# ==========================
# BROADCAST TO ALL CLIENTS
# ==========================
async def broadcast(msg: str):
    if not clients:
        return

    dead_clients = []

    for c in clients:
        try:
            await c.send(msg)
        except:
            dead_clients.append(c)

    for c in dead_clients:
        clients.remove(c)


# ==========================
# NATS HANDLER
# ==========================
async def nats_handler(msg):
    data = msg.data.decode()
    # Print face not detected message to terminal
    if data == 'no_face':
        print("\n" + "=" * 60)
        print("FACE NOT DETECTED (from NATS)")
        print("=" * 60 + "\n")
    await broadcast(data)


# ==========================
# MAIN
# ==========================
async def main():
    nc = NATS()

    await nc.connect("nats://192.168.0.187:4222")

    await nc.subscribe("vision.eye.test.ready", cb=nats_handler)
    await nc.subscribe("vision.eye.distance.status", cb=nats_handler)
    await nc.subscribe("vision.eye.cam0.depth", cb=nats_handler)
    await nc.subscribe("vision.eye.cam0.face", cb=nats_handler)

    server = await websockets.serve(ws_handler, "localhost", 8765)

    print("Bridge running at ws://localhost:8765")

    await server.wait_closed()


asyncio.run(main())