
import azure.functions as func
import datetime
import json
import logging
import os
import uuid

from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# Azure Storage configuration
STORAGE_CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
CONTAINER_NAME = "sensor-readings"

# IoT Hub built-in Event Hubs-compatible endpoint
EVENT_HUB_NAME = "iothub-ehub-smartgarde-74484921-fe51b32700"


@app.event_hub_message_trigger(
    arg_name="event",
    event_hub_name=EVENT_HUB_NAME,
    connection="IoTHubEventHubConnection",
    consumer_group="smartgarden-functions"
)
def process_sensor_reading(event: func.EventHubEvent):
    try:
        # Read the incoming sensor message
        message_body = event.get_body().decode("utf-8")
        reading = json.loads(message_body)

        logging.info("Received sensor reading: %s", message_body)

        # Check that the required sensor values exist
        required_fields = [
            "soilMoisture",
            "temperature",
            "sunlight"
        ]

        for field in required_fields:
            if field not in reading:
                raise ValueError(f"Missing sensor field: {field}")

        # Check Azure Storage configuration
        if not STORAGE_CONNECTION_STRING:
            raise ValueError("Azure Storage connection is missing")

        # Connect to Blob Storage
        blob_service = BlobServiceClient.from_connection_string(
            STORAGE_CONNECTION_STRING
        )

        container_client = blob_service.get_container_client(
            CONTAINER_NAME
        )

        # Create a unique JSON filename
        now = datetime.datetime.now(datetime.timezone.utc)

        blob_name = (
            f"{now:%Y/%m/%d}/"
            f"{now:%H%M%S}_{uuid.uuid4().hex}.json"
        )

        # Save the sensor reading
        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(
            json.dumps(reading, indent=4),
            overwrite=False
        )

        logging.info("Sensor reading saved: %s", blob_name)

        # Check for low soil moisture
        soil_moisture = float(reading["soilMoisture"])

        if soil_moisture < 30:
            logging.warning(
                "LOW MOISTURE ALERT! Soil moisture is %.1f%%",
                soil_moisture
            )

    except Exception:
        logging.exception("Failed to process sensor reading")
        raise
