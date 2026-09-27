"""
GPS Simulator: publishes fake, moving vehicle coordinates to
vehicles/{vehicle_id}/gps over MQTT, walking the vehicle's route
point-by-point in a loop.

It fetches its own route from the backend API so it never needs
hardcoded coordinates (mirrors the "no hardcoded coordinates" rule
that applies to the Flutter app).
"""
import json
import logging
import math
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [simulator] %(message)s")
logger = logging.getLogger("simulator")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
VEHICLE_ID = int(os.getenv("VEHICLE_ID", "1"))
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
SIM_USERNAME = os.getenv("SIM_USERNAME", "user1")
SIM_PASSWORD = os.getenv("SIM_PASSWORD", "password1")

# Fallback route if the API isn't reachable (e.g. running the simulator standalone).
FALLBACK_ROUTE = [
    {"latitude": 27.3389, "longitude": 88.6065},
    {"latitude": 27.3400, "longitude": 88.6080},
    {"latitude": 27.3415, "longitude": 88.6100},
    {"latitude": 27.3430, "longitude": 88.6120},
    {"latitude": 27.3445, "longitude": 88.6140},
]


def fetch_route_points() -> list[dict]:
    """Log in as the vehicle's assigned user and pull their route points."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": SIM_USERNAME, "password": SIM_PASSWORD},
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]

        points_resp = requests.get(
            f"{BACKEND_URL}/api/routes/me/points",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        points_resp.raise_for_status()
        points = points_resp.json()
        if points:
            logger.info("Fetched %d route points from backend", len(points))
            return points
    except Exception as e:
        logger.warning("Could not fetch route from backend (%s), using fallback route", e)

    return FALLBACK_ROUTE


def interpolate(p1: dict, p2: dict, fraction: float) -> dict:
    lat = p1["latitude"] + (p2["latitude"] - p1["latitude"]) * fraction
    lon = p1["longitude"] + (p2["longitude"] - p1["longitude"]) * fraction
    return {"latitude": lat, "longitude": lon}


def haversine_km(p1: dict, p2: dict) -> float:
    R = 6371.0
    lat1, lon1 = math.radians(p1["latitude"]), math.radians(p1["longitude"])
    lat2, lon2 = math.radians(p2["latitude"]), math.radians(p2["longitude"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def main():
    route_points = fetch_route_points()
    if len(route_points) < 2:
        logger.error("Need at least 2 route points to simulate movement, exiting.")
        return

    client = mqtt.Client(client_id=f"gps-simulator-vehicle-{VEHICLE_ID}")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    topic = f"vehicles/{VEHICLE_ID}/gps"
    logger.info("Publishing to %s every %ss", topic, PUBLISH_INTERVAL)

    segment_index = 0
    steps_per_segment = 5  # interpolation steps between two consecutive route points
    step = 0

    try:
        while True:
            p1 = route_points[segment_index % len(route_points)]
            p2 = route_points[(segment_index + 1) % len(route_points)]

            fraction = step / steps_per_segment
            position = interpolate(p1, p2, fraction)

            distance_km = haversine_km(p1, p2) / steps_per_segment
            speed_kmh = round((distance_km / (PUBLISH_INTERVAL / 3600)), 1) if PUBLISH_INTERVAL > 0 else 0

            payload = {
                "latitude": round(position["latitude"], 6),
                "longitude": round(position["longitude"], 6),
                "speed": speed_kmh,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            client.publish(topic, json.dumps(payload), qos=1)
            logger.info("Published: %s", payload)

            step += 1
            if step > steps_per_segment:
                step = 0
                segment_index += 1

            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down simulator.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
