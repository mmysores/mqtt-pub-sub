
# # # mtconnect_subscriber.py

# import csv                     # for writing rows of data to a CSV file
# import json                    # for parsing JSON-formatted MQTT messages
# import logging                 # for logging informational and error messages
# from paho.mqtt import client as mqtt  # import the MQTT client class

# # MQTT broker address (public HiveMQ broker)
# MQTT_BROKER = "broker.hivemq.com"
# # MQTT port (1883 is the standard unencrypted MQTT port)
# MQTT_PORT   = 1883
# # Topic on which the publisher is sending spindle-speed data
# MQTT_TOPIC  = "UMC750/spindleSpeed"

# # Filename for the local CSV where we append each record
# CSV_FILE    = "spindle_speed_log.csv"

# # Configure logging: show INFO and higher, include timestamp and level in each entry
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s: %(message)s"
# )

# # Instantiate the MQTT client; using default callback_api v1
# sub = mqtt.Client("Subscriber")

# def on_connect(client, userdata, flags, rc):
#     """
#     Called when the client connects (or fails to) the MQTT broker , rc == 0 means “connected OK.”
#     """
#     if rc == 0:
#         logging.info("Connected to MQTT broker — subscribing to %s", MQTT_TOPIC)
#         # Subscribe with QoS=1 to ensure at least-once delivery
#         client.subscribe(MQTT_TOPIC, qos=1)
#     else:
#         logging.error("Failed to connect to MQTT broker (rc=%s)", rc)

# def on_message(client, userdata, msg):
#     """
#     Called whenever a message arrives on a subscribed topic.
#       - msg.topic is the topic name.
#       - msg.payload is the raw message bytes.
#     """
#     try:
#         # Decode bytes → string, then parse JSON into a dict
#         data = json.loads(msg.payload.decode("utf-8"))
#         # Extract the fields we care about
#         timestamp     = data["timestamp"]      # e.g. "2025-05-31T12:00:00Z"
#         spindle_speed = data["spindle_speed"]  # e.g. 1500.0

#         # Prepare one CSV row; order is up to you
#         row = [timestamp, spindle_speed]
#     except Exception as e:
#         # If parsing fails or keys are missing, log and skip
#         logging.error("Bad message payload: %s", e)
#         return

#     # Append the new row to our CSV file
#     with open(CSV_FILE, "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(row)

#     # Log what we wrote
#     logging.info("Logged: %s", row)

# # Hook up our callback functions
# sub.on_connect = on_connect
# sub.on_message = on_message

# if __name__ == "__main__":
#     # Connect to the MQTT broker at the given host/port
#     sub.connect(MQTT_BROKER, MQTT_PORT)
#     # Enter a blocking network loop; handles reconnects and dispatches callbacks
#     sub.loop_forever()











# Starting here for availability

import csv
import json
import logging
from paho.mqtt import client as mqtt


MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "UMC750/availability"
CSV_FILE    = "availability_log.csv"

# Logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# Create an MQTT client for subscribing
sub = mqtt.Client("Subscriber")

def on_connect(client, userdata, flags, rc):
    """Called on (re)connect—subscribe if we connected OK."""
    if rc == 0:
        logging.info("Connected to MQTT; subscribing to %s", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error("MQTT connect failed (rc=%s)", rc)

def on_message(client, userdata, msg):
    """Called whenever a message arrives on the subscribed topic."""
    try:
        # Decode JSON payload into a dict
        data = json.loads(msg.payload.decode())
        row  = [data["timestamp"], data["availability"]]
    except Exception as e:
        logging.error("Malformed message: %s", e)
        return

    # Append the row to our CSV file
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    logging.info("Logged to CSV: %s", row)

# Hook up callbacks
sub.on_connect = on_connect
sub.on_message = on_message

if __name__ == "__main__":
    try:
        sub.connect(MQTT_BROKER, MQTT_PORT)
        sub.loop_forever()
    except KeyboardInterrupt:
        logging.info("Interrupted by user; exiting")
    finally:
        sub.disconnect()
