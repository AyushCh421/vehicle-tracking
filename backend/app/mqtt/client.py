"""
MQTT listener: subscribes to vehicles/{vehicle_id}/gps and stores incoming
GPS readings. Runs in a background thread started/stopped from main.py's
FastAPI lifespan hooks, so it doesn't block the API event loop.
"""
import json
import logging
import re
import threading

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.gps import GPSMessage
from app.services.gps_service import ingest_gps_reading

logger = logging.getLogger("mqtt_client")

TOPIC_RE = re.compile(r"^vehicles/(\d+)/gps$")


class MQTTIngestor:
    def __init__(self) -> None:
        self._client = mqtt.Client(client_id="gps-tracking-backend", clean_session=True)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._thread: threading.Thread | None = None

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker %s:%s", settings.MQTT_BROKER, settings.MQTT_PORT)
            client.subscribe(settings.MQTT_GPS_TOPIC_FILTER, qos=1)
        else:
            logger.error("MQTT connection failed with code %s", rc)

    def _on_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker (rc=%s)", rc)

    def _on_message(self, client, userdata, msg):
        match = TOPIC_RE.match(msg.topic)
        if not match:
            logger.debug("Ignoring message on unexpected topic %s", msg.topic)
            return

        vehicle_id = int(match.group(1))

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("Malformed JSON payload on %s", msg.topic)
            return

        try:
            gps_message = GPSMessage(**payload)
        except ValidationError as e:
            logger.warning("Invalid GPS payload on %s: %s", msg.topic, e)
            return

        try:
            stored = ingest_gps_reading(vehicle_id, gps_message)
            if stored:
                logger.info(
                    "Stored GPS reading: vehicle_id=%s lat=%s lon=%s speed=%s",
                    vehicle_id, gps_message.latitude, gps_message.longitude, gps_message.speed,
                )
        except Exception:
            logger.exception("Failed to ingest GPS reading for vehicle_id=%s", vehicle_id)

    def start(self) -> None:
        def _run():
            while True:
                try:
                    self._client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
                    self._client.loop_forever(retry_first_connection=True)
                except Exception:
                    logger.exception("MQTT loop crashed, retrying in 5s")
                    import time
                    time.sleep(5)

        self._thread = threading.Thread(target=_run, name="mqtt-ingestor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            self._client.disconnect()
        except Exception:
            pass


mqtt_ingestor = MQTTIngestor()
