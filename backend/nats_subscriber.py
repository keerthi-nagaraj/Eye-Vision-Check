import asyncio
import json
from nats.aio.client import Client as NATS

face_detected = False
distance_value = None
VISION_READY_TOPIC = "vision.eye.test.ready"
DISTANCE_STATUS_TOPIC = "vision.eye.distance.status"
PERFECT_DISTANCE = 130
TOLERANCE = 50  # 100-160cm range


# Function to get distance status
def get_distance_status(face_detected, distance_value):
    if not face_detected:
        return "no_face"
    if distance_value is None:
        return "no_distance"
    if distance_value < (PERFECT_DISTANCE - TOLERANCE): # checks if distance is less than 110cm
        return "too_near"
    elif distance_value > (PERFECT_DISTANCE + TOLERANCE): # checks if distance is more than 150cm
        return "too_far"
    else:
        return "perfect"


def is_ready(face_detected, distance_value):
    status = get_distance_status(face_detected, distance_value)
    return status == "perfect"


def estimate_distance(depth):
    try:
        return float(depth["mean"])
    except:
        return None


async def handler(msg):
    global face_detected, distance_value, nc

    subject = msg.subject
    data = msg.data.decode()

    print("\n" + "=" * 60)
    print("Subject:", subject)

    # ---------------- FACE ----------------
    if subject == "vision.eye.cam0.face":
        try:
            j = json.loads(data)
            face_detected = bool(j.get("face_detected", False))
            # Check for face count if available
            face_count = j.get("face_count", 1)
        except:
            face_detected = data.strip().lower() == "true"
            face_count = 1

        # ✅ REQUIRED OUTPUT FORMAT
        if face_detected:
            if face_count == 1:
                print("1 FACE DETECTED")
            else:
                print(f"{face_count} FACES DETECTED (WARNING: Only 1 face should be detected)")
        else:
            print("NO FACE DETECTED")

        # Only consider it valid if exactly 1 face is detected
        face_detected = face_detected and face_count == 1

        # Publish updated ready status
        ready = is_ready(face_detected, distance_value)
        await nc.publish(
            VISION_READY_TOPIC,
            b"true" if ready else b"false"
        )

        # Publish distance status
        status = get_distance_status(face_detected, distance_value)
        print("Publishing distance status:", status)
        await nc.publish(
            DISTANCE_STATUS_TOPIC,
            status.encode()
        )

    # ---------------- DEPTH ----------------
    elif subject == "vision.eye.cam0.depth":
        try:
            j = json.loads(data)
            distance_value = estimate_distance(j)
            print("Distance:", distance_value)
        except:
            print("Distance: NOT AVAILABLE")

        # Publish updated ready status
        ready = is_ready(face_detected, distance_value)
        await nc.publish(
            VISION_READY_TOPIC,
            b"true" if ready else b"false"
        )

        # Publish distance status
        status = get_distance_status(face_detected, distance_value)
        await nc.publish(
            DISTANCE_STATUS_TOPIC,
            status.encode()
        )

    print("=" * 60)


async def main():
    global nc
    nc = NATS()    
    
    await nc.connect("nats://192.168.0.187:4222")
    ready = is_ready(face_detected, distance_value)

    await nc.publish(
        "vision.eye.>",
        b"true" if ready else b"false"
    )

    await nc.subscribe("vision.eye.cam0.face", cb=handler)
    await nc.subscribe("vision.eye.cam0.depth", cb=handler)

    print("Listening only to face + depth...")

    while True:
        await asyncio.sleep(1)


asyncio.run(main())