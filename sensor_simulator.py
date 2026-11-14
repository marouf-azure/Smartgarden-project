import os
import random
import time
import json
from datetime import datetime, timezone
from azure.iot.device import IoTHubDeviceClient, Message
from dotenv import load_dotenv


load_dotenv()
# --- CONFIGURATION ---
# Paste your connection string from Azure here:
CONNECTION_STRING = os.getenv("AZURE_IOT_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("Azure IoT connection string is missing!")

DEVICE_ID = "gardensensor1"
def main():
    print("SMART GARDEN MONITOR")
    print("Connecting to Azure IoT Hub...")
    
    # Create the IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    client.connect()
    print("Connected successfully!")
    print("--------------------------------")

    try:
        while True:
            # Generate imaginary sensor readings
            soil_moisture = random.randint(10, 100)
            temperature = random.randint(18, 40)
            sunlight = random.randint(0, 100)

            # Prepare the sensor information
            sensor_data = {
                "deviceId": DEVICE_ID,
                "soilMoisture": soil_moisture,
                "temperature": temperature,
                "sunlight": sunlight,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Convert to JSON string
            message_body = json.dumps(sensor_data)
            
            # Create the Azure message
            message = Message(message_body)
            message.content_encoding = "utf-8"
            message.content_type = "application/json"

            # Send the message to Azure
            client.send_message(message)
            
            print(f"Sent to Azure: {message_body}")

            if soil_moisture < 30:
                print("LOCAL ALERT: Your plant needs water!")

            print("--------------------------------")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping simulator...")
    finally:
        client.shutdown()

if __name__ == "__main__":
    main()